from __future__ import print_function

import csv
import json
import os
import sys
import requests

from ccc_client.utils import parseAuthToken


class EveMongoRunner(object):

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
        self.headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.authToken}

    def get_status(self):
        url = "{}/v0/status".format(self.url)
        r = requests.get(url=url)
        return r

    def query(self, endpoint, filter=None):
        url = '{}/v0/{}'.format(self.url, endpoint)
        r = requests.get(url=url, data=json.dumps(filter), headers=self.headers)
        return r

    # @classmethod
    def publish_batch(self, tsv, siteId, user, programCode, projectCode, domainName, domainFile=None):

        # Note: this creates the opportunity to allow externally provided field
        # definitions, or potentially a different schema at runtime
        if domainFile is None:
            ddFile = os.path.dirname(os.path.realpath(__file__))
            ddFile = ddFile + "/../resources/evemongo_domains.json"
        else:
            ddFile = domainFile

        with open(ddFile) as json_data:
            self.DomainDescriptors = json.load(json_data)

        # If domainFile doesn't contain given domain, process will fail
        if domainName not in self.DomainDescriptors:
            raise RuntimeError("Unknown domain: " + domainName)

        # Parse TSV
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
                                               self.headers,
                                               self.url,
                                               self.DomainDescriptors)
                else:
                    response.append(rowParser.pushArrToEveMongo(row))
                i += 1
        return response

    # Responsible for inspecting the header and normalizing/augmenting field
    # names
    class RowParser(object):
        def __init__(self, fileHeader=None, siteId=None, user=None, programCode=None,
                     projectCode=None, domainName=None, headers=None, url=None,
                     domainDescriptors=None):

            self.fileHeader = fileHeader
            self.siteId = siteId
            self.user = user
            self.programCode = programCode
            self.projectCode = projectCode
            self.domainName = domainName
            self.headers = headers
            self.url = url
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases()

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

            # Note: According to the GDC API, the API endpoint url follows the format:
            # "[base_host]/[API_version]/submission/[programName]/[projectCode]".
            # We will need to decide what constitutes 'program' and 'project' in our database.
            url = "{}/v0/submission/{}/{}".format(self.url, self.programCode, self.projectCode)
            r = requests.post(url=url, data=json.dumps(rowMap, sort_keys=True), headers=self.headers)
            return r