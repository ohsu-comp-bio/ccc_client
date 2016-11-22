from __future__ import print_function

import csv
import json
import os
import sys
import requests
import re

from ccc_client import DtsRunner
from ccc_client.utils import parseAuthToken


class EveMongoRunner(object):
    __domainFile = None

    def __init__(self, host=None, port=None, authToken=None):
        if not host:
            host = "http://192.168.99.100"
        if not port:
            port = "8000"
        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.url = "{}:{}".format(host, port)
        self.req = requests.Session()
        self.req.headers = {'Authorization': 'Bearer ' + self.authToken}
        self.readDomainDescriptors()

    # Note: this creates the opportunity to allow externally provided field
    # definitions, or potentially a different schema at runtime
    def readDomainDescriptors(self):
        if self.__domainFile is None:
            ddFile = os.path.dirname(os.path.realpath(__file__))
            ddFile = ddFile + "/resources/evemongo_domains.json"
        else:
            ddFile = self.__domainFile

        with open(ddFile) as json_data:
            self.DomainDescriptors = json.load(json_data)

    # @classmethod
    def setDomainDescriptors(self, domainFile):
        self.__domainFile = domainFile
        self.readDomainDescriptors()

    # @classmethod
    def publish_batch(self, tsv, siteId, user, programCode, projectCode, domainName, isMock,
                      skipDtsRegistration):

        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

        read_mode = 'rb' if sys.version_info[0] < 3 else 'r'
        i = 0
        with open(tsv, mode=read_mode) as infile:
            response = []
            reader = csv.reader(infile, delimiter='\t')
            for row in reader:
                if i == 0:
                    rowParser = self.RowParser(row,
                                               siteId,
                                               user,
                                               programCode,
                                               projectCode,
                                               domainName,
                                               self.req,
                                               self.url,
                                               self.DomainDescriptors,
                                               isMock,
                                               skipDtsRegistration)
                else:
                    response.append(rowParser.pushArrToEveMongo(row))
                i += 1
        return response

    def __process_fields(self, fields):
        pfields = {}
        if isinstance(fields, str):
            pfields.update(self.__validate_field(fields))
        elif isinstance(fields, (list, tuple)):
            for f in fields:
                pfields.update(self.__process_fields(f))
        elif isinstance(fields, dict):
            pfields.update(fields)
        else:
            raise TypeError("queries must be a str or list type")
        return pfields

    def __validate_field(self, field):
        assert re.search(":", field) is not None
        assert len(re.findall(":", field)) == 1
        key, val = re.compile("\s*:\s*").split(field)
        return {key: val}

    # Responsible for inspecting the header and normalizing/augmenting field
    # names
    class RowParser(object):
        def __init__(self, fileHeader=None, siteId=None, user=None, programCode=None,
                     projectCode=None, domainName=None, req=None, url=None,
                     domainDescriptors=None, isMock=False,
                     skipDtsRegistration=False):

            self.fileHeader = fileHeader
            self.siteId = siteId
            self.user = user
            self.programCode = programCode
            self.projectCode = projectCode
            self.domainName = domainName
            self.req = req
            self.url = url
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases()
            self.isMock = isMock
            if isMock:
                self.skipDtsRegistration = True
            else:
                self.skipDtsRegistration = skipDtsRegistration

        def getAliases(self):
            aliasMap = []
            fds = self.domainDescriptors[self.domainName]["fieldDescriptors"]
            for fieldName in fds.keys():
                field = fds[fieldName]
                if "aliases" in field.keys():
                    for alias in field["aliases"]:
                        aliasMap.append([alias.lower(), fieldName])
            return aliasMap

        def generateRowMapFromArr(self, rowArr):
            if not rowArr:
                raise ValueError("row cannot be empty")
            elif len(rowArr) != len(self.fileHeader):
                raise ValueError("fileHeader and row must have the same number of items")
            else:
                ret = dict(zip(self.fileHeader, rowArr))
                return ret

        def processRowMap(self, rowMap):
            # get all fields for domain
            fds = self.domainDescriptors[self.domainName]["fieldDescriptors"]

            # iterate over rowMap
            rowMap_keys = list(rowMap.keys())
            for token in rowMap_keys:
                val = rowMap[token]
                cannonicalName = []
                # append known aliases
                for i in self.aliasMap:
                    if token.lower() == i[0]:
                        cannonicalName.append(i[1])
                    else:
                        cannonicalName.append(token)
                for i in cannonicalName:
                    if i in fds.keys():
                        # allow for text on missing value
                        if val is None:
                            if 'missingValue' in fds[i].keys():
                                val = fds[i]['missingValue']
                        else:
                            # datatype conversion:
                            if 'dataType' in fds[i].keys():
                                dtype = fds[i]['dataType']
                                if dtype == 'int':
                                    val = int(val)
                                elif dtype == 'float':
                                    val = float(val)
                                elif dtype == 'dict':
                                    val = {fds[i]['dict_key']: val}
                                elif dtype == 'string':
                                    pass
                                else:
                                    raise TypeError(
                                        "Unable to convert field: " + token +
                                        " to type: " + dtype +
                                        " for value [" + val + "]"
                                    )
                    # finally append value
                    rowMap[token] = val

                    # keep token and alias
                    if token != i:
                        rowMap[i] = val

            if self.domainName.lower() == 'resource' or self.domainName.lower() == 'file':
                # process filepath/ccc_id
                if not self.skipDtsRegistration:
                    rowMap = self.validateOrRegisterWithDts(rowMap)

            # NOTE: these should always supersede the previous properties
            if self.domainName.lower() == 'case':
                rowMap['projects'] = {"code": self.projectCode}
            rowMap['siteId'] = self.siteId
            rowMap['projectCode'] = self.projectCode
            rowMap['type'] = self.domainName
            return rowMap

        def pushArrToEveMongo(self, row):
            rowMap = self.generateRowMapFromArr(row)
            return self.pushMapToEveMongo(rowMap)

        def pushMapToEveMongo(self, rowMap):
            rowMap = self.processRowMap(rowMap)

            if self.isMock:
                return rowMap
            else:
                # Note: According to the GDC API, the API endpoint url follows the format:
                # "[base_host]/[API_version]/submission/[programName]/[projectCode]".
                # We will need to decide what constitutes 'program' and 'project' in our database.
                url = "{}/v0/submission/{}/{}".format(self.url, self.programCode, self.projectCode)
                r = self.req.post(url=url, json=rowMap)
                return r

        def validateOrRegisterWithDts(self, rowMap):
            path = self.__check_resource_path(rowMap)
            if 'ccc_id' in rowMap.keys():
                self.validateCccId(rowMap['ccc_id'], path)
            else:
                rowMap['ccc_id'] = self.registerWithDts(path)
            return rowMap

        def registerWithDts(self, filepath):
            dts = DtsRunner()
            response = dts.post(filepath,
                                self.siteId,
                                self.user)
            if response.status_code // 100 != 2:
                raise RuntimeError("DTS registration for " + filepath + " failed")
            else:
                return response.text

        def validateCccId(self, ccc_id, filepath):
            dts = DtsRunner()
            response = dts.get(ccc_id)
            if response.status_code // 100 != 2:
                raise RuntimeError("CCC_ID not found: " + ccc_id)
            else:
                data = response.json()
                assert data['name'] == os.path.basename(filepath)
                assert data['path'] == os.path.dirname(filepath)
                return True

        def __check_resource_path(self, rowMap):
            if 'filepath' in rowMap.keys():
                path = rowMap['filepath']
            elif 'url' in rowMap.keys():
                path = rowMap['url']
            else:
                raise KeyError(
                    "Resource registration or validation with the DTS requires a valid file path or url"
                )
            return path
