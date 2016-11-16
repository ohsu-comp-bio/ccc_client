from __future__ import print_function

import csv
import json
import os
import re
import sys

from ccc_client import DtsRunner
from ccc_client.utils import parseAuthToken
from elasticsearch import Elasticsearch

import requests

class ElasticSearchRunner(object):
    __domainFile = None

    def __init__(self, host=None, port=None, authToken=None):
        if host is not None:
            self.host = host
        else:
            self.host = "localhost"

        if port is not None:
            self.port = port
        else:
            self.port = "9200"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        # Requests Session object appears incapable of holding host/url name;
        # Will need to pass 'url="{}.{}".format(self.host, self.port)' to batch post.
        self.req = requests.Session()
        self.req.headers = {'Authorization': 'Bearer ' + self.authToken}
        self.es = Elasticsearch(hosts="{0}:{1}".format(self.host, self.port))
#         # see:
#         # https://discuss.elastic.co/t/how-do-i-add-a-custom-http-header-using-the-python-client/38907
        self.es.transport.connection_pool.connection.headers.update({'Authorization': 'Bearer ' + self.authToken})
        self.readDomainDescriptors()

    # Note: this creates the opportunity to allow externally provided field
    # definitions, or potentially a different schema at runtime
    def readDomainDescriptors(self):
        if self.__domainFile is None:
            ddFile = os.path.dirname(os.path.realpath(__file__))
            ddFile = ddFile + "/resources/domains.json"
        else:
            ddFile = self.__domainFile

        with open(ddFile) as json_data:
            self.DomainDescriptors = json.load(json_data)
            json_data.close()


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
                                               # self.domain,
                                               self.es,
                                               self.req,
                                               self.host,
                                               self.port,
                                               self.DomainDescriptors,
                                               isMock,
                                               skipDtsRegistration)
                else:
                    response.append(rowParser.pushArrToElastic(row))
                i += 1
        return response


    # Responsible for inspecting the header and normalizing/augmenting field
    # names
    class RowParser(object):
        def __init__(self, fileHeader=None, siteId=None, user=None, programCode=None,
                     projectCode=None, domainName=None, es=None, req=None, host=None, port=None,
                     domainDescriptors=None, isMock=False,
                     skipDtsRegistration=False):

            self.fileHeader = fileHeader
            self.siteId = siteId
            self.user = user
            self.programCode = programCode
            self.projectCode = projectCode
            self.domainName = domainName
            self.es = es
            self.req = req
            self.host = host
            self.port = port
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases(fileHeader)
            self.isMock = isMock
            if isMock:
                self.skipDtsRegistration = True
            else:
                self.skipDtsRegistration = skipDtsRegistration

        def getAliases(self, fileHeader):
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

            if self.domainName.lower() == 'case':
                rowMap['projects'] = {"code": self.projectCode}

            # denormalize resources
            if self.domainName.lower() == 'resource' or self.domainName.lower() == 'file':
                # process filepath/ccc_id
                if not self.skipDtsRegistration:
                    rowMap = self.validateOrRegisterWithDts(rowMap)
                # append fields from other domains (denormalize)
                domainsToAppend = list(self.domainDescriptors.keys())
                # if not self.domain:
                domainsToAppend.remove(self.domainName)
                # else:
                #     domainsToAppend.remove('Resource')
                for dn in domainsToAppend:
                    rowMap = self.appendFieldsForDomain(rowMap, dn)

            # NOTE: these should always supersede the previous properties
            rowMap['siteId'] = self.siteId
            rowMap['projectCode'] = self.projectCode
            rowMap['type'] = self.domainName
            return rowMap

        def appendFieldsForDomain(self, rowMap, dn):
            if self.domainDescriptors[dn]['keyField'] in rowMap:
                key = self.generateKeyForDomain(rowMap, dn, True)
                domain = self.domainDescriptors[dn]
                # index = self.getIndexNameForDomain(dn)
                endpoint = domain['docType'] + 's'
                # body = {
                #     "size": 10000, "query": {
                #         "query_string": {
                #             "query": "_id" + ":\"" + key + "\""
                #         }
                #     }
                # }
                # body = {"id": key}
                # url = "http://{}:{}/v0/{}".format(self.host, self.port, endpoint)
                # hits = self.req.get(url=url, json=body)

                # hits = self.es.search(
                #     index=self.getIndexNameForDomain(dn),
                #     doc_type=domain['docType'],
                #     ignore_unavailable=True,
                #     body={
                #         "size": 10000, "query": {
                #             "query_string": {
                #                 "query": "_id" + ":\"" + key + "\""
                #             }
                #         }
                #     }
                # )

                # TO DO // Fix issue where search returns all possibilities. When fixed uncomment below
                # hits = hits.json()['data']['hits']
                # if len(hits) > 0:
                #     hit = hits[0]
                #     rowMap.update(hit["_source"])

            return rowMap

        def generateKeyForDomain(self, rowMap, domainName, r=False):
            domain = self.domainDescriptors[domainName]
            keyField = domain['keyField']

            if keyField not in rowMap:
                print('exception:', file=sys.stderr)
                print(json.dumps(rowMap), file=sys.stderr)
                raise KeyError("Row lacks key field: " + keyField)

            if 'unmatchedInheritance' in domain.keys() and r == True:
                if domainName == 'case':
                    return rowMap["_".join(['individual', keyField]).lower()]
            elif 'useKeyFieldAsIndexKey' in domain.keys():
                return (rowMap[keyField]).lower()
            else:
                domainKey = "-".join(
                    [self.projectCode, domainName, rowMap[keyField]]
                ).lower()
                return domainKey

        def getIndexNameForDomain(self, domainName):
            if not self.domain:
                domain = self.domainDescriptors[domainName]
            else:
                domain = self.domain
            return "-".join([self.projectCode, domain['indexPrefix']]).lower()

        def getCollectionNameForDomain(self, domainName):
            # if not self.domain:
            domain = self.domainDescriptors[domainName]
            return self.programCode

        def pushArrToElastic(self, row):
            rowMap = self.generateRowMapFromArr(row)
            return self.pushMapToElastic(rowMap)

        def pushMapToElastic(self, rowMap):
            rowMap = self.processRowMap(rowMap)

            if self.isMock:
                return rowMap
            else:
                # Note: According to the GDC API, the API endpoint url follows the format:
                # "[base_host]/[API_version]/submission/[programName]/[projectCode]".
                # We will need to decide what constitutes 'program' and 'project' in our database.
                coll = self.getCollectionNameForDomain(self.domainName)
                project = self.projectCode
                doc_type = self.domainDescriptors[self.domainName]['docType']
                doc_id = self.generateKeyForDomain(rowMap, self.domainName)
                r = self.req.post(url="http://{}:{}/v0/submission/{}/{}".format(self.host, self.port, coll, project),
                                         json=rowMap)
                
                return r.json()

#         def validateOrRegisterWithDts(self, rowMap):
#             path = self.__check_resource_path(rowMap)
#             if 'ccc_id' in rowMap.keys():
#                 self.validateCccId(rowMap['ccc_id'], path)
#             else:
#                 rowMap['ccc_id'] = self.registerWithDts(path)
#             return rowMap
#
#         def registerWithDts(self, filepath):
#             dts = DtsRunner()
#             response = dts.post(filepath,
#                                 self.siteId,
#                                 self.user)
#             if response.status_code // 100 != 2:
#                 raise RuntimeError("DTS registration for " + path + " failed")
#             else:
#                 return response.text
#
#         def validateCccId(self, ccc_id, filepath):
#             dts = DtsRunner()
#             response = dts.get(ccc_id)
#             if response.status_code // 100 != 2:
#                 raise RuntimeError("CCC_ID not found: " + ccc_id)
#             else:
#                 data = response.json()
#                 assert data['name'] == os.path.basename(filepath)
#                 assert data['path'] == os.path.dirname(filepath)
#                 return True
#
#         def __check_resource_path(self, rowMap):
#             if 'filepath' in rowMap.keys():
#                 path = rowMap['filepath']
#             elif 'url' in rowMap.keys():
#                 path = rowMap['url']
#             else:
#                 raise KeyError(
#                     "Resource registration or validation with the DTS requires a valid file path or url"
#                 )
#             return path
