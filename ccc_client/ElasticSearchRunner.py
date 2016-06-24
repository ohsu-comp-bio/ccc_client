from __future__ import print_function

import csv
import json
import os
import sys
import uuid
import ccc_client.DtsRunner
from ccc_client.utils import parseAuthToken
from elasticsearch import Elasticsearch


class ElasticSearchRunner(object):
    __domainFile = None

    def __init__(self, host=None, port=None, authToken=None):
        if host is not None:
            self.host = host
        else:
            self.host = "0.0.0.0"

        if port is not None:
            self.port = port
        else:
            self.port = "9200"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.es = Elasticsearch(hosts="{0}:{1}".format(self.host, self.port))
        # see:
        # https://discuss.elastic.co/t/how-do-i-add-a-custom-http-header-using-the-python-client/38907
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
    def setDomainDescriptors(self, domainFile):
        self.__domainFile = domainFile
        self.readDomainDescriptors()

    # @classmethod
    def query(self, domainName, queries, output=None):
        terms = []
        for query in queries:
            vals = query.split(":")
            terms.append({
                "match_phrase": {
                    vals[0]: vals[1]
                }
            })

        body = {
            "size": 10000,
            "query": {
                "bool": {
                    "must": {
                        "and": terms
                    }
                }
            },
        }

        domain = self.DomainDescriptors[domainName]
        hits = self.es.search(
            index=("*-" + domainName).lower(),
            doc_type=domain['docType'],
            ignore_unavailable=True,
            allow_no_indices=True,
            body=body
        )

        hits = hits['hits']['hits']
        ret = []
        if hits:
            for hit in hits:
                ret.append(hit['_source'])

        if output is not None:
            with open(output, 'w') as outfile:
                outfile.write(json.dumps(ret))
        else:
            print(ret)

    # @classmethod
    def publish_resource(self, filePath, siteId, user, projectCode, workflowId,
                         mimeType, domainName, inheritFrom, properties, isMock):
        rowMap = {}

        if (inheritFrom):
            domain = self.DomainDescriptors[domainName]
            hits = self.es.search(
                index=("*-" + domainName).lower(),
                doc_type=domain['docType'],
                ignore_unavailable=True,
                allow_no_indices=True,
                body={
                    "size": 10,
                    "query": {
                        "bool": {
                            "must": {
                                "match_phrase": {
                                    "ccc_id": inheritFrom
                                }
                            }
                        }
                    }
                }
            )

            hits = hits['hits']['hits']
            if hits:
                # apply data
                hit = hits[0]
                if ("_source" in hit.keys()):
                    rowMap.update(hit["_source"])
            else:
                raise RuntimeError(
                    "Unable to find existing resource with id: " + inheritFrom
                )

        for prop in properties:
            tokens = prop.split(":")
            rowMap[tokens[0]] = tokens[1]

        # NOTE: these should always supersede the properties argument
        rowMap['filepath'] = filePath
        rowMap['siteId'] = siteId
        rowMap['projectCode'] = projectCode
        rowMap['workflowId'] = workflowId
        rowMap['mimetype'] = mimeType

        rowParser = self.RowParser(rowMap.keys(), siteId, user, projectCode,
                                   'resource', self.es, self.DomainDescriptors,
                                   isMock)
        rowParser.pushMapToElastic(rowMap)

        return rowMap

    # @classmethod
    def print_domain(self, domainName):
        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

        domain = self.DomainDescriptors[domainName]
        print(domain)

    # @classmethod
    def publish_batch(self, tsv, siteId, user, projectCode, domainName, isMock):
        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

        read_mode = 'rb' if sys.version_info[0] < 3 else 'r'
        i = 0
        with open(tsv, mode=read_mode) as infile:
            reader = csv.reader(infile, delimiter='\t')
            for row in reader:
                if i == 0:
                    rowParser = self.RowParser(row,
                                               siteId,
                                               user,
                                               projectCode,
                                               domainName, self.es,
                                               self.DomainDescriptors,
                                               isMock)
                else:
                    rowParser.pushArrToElastic(row)

                i += 1

    # Responsible for inspecting the header and normalizing/augmenting field
    # names
    class RowParser(object):
        # array of raw data
        fileHeader = None
        siteId = None
        user = None
        aliasMap = {}
        domainName = None
        es = None
        domainDescriptors = None
        isMock = False

        def __init__(self, fileHeader=None, siteId=None, user=None,
                     projectCode=None, domainName=None, es=None,
                     domainDescriptors=None, isMock=False):
            self.fileHeader = fileHeader
            self.siteId = siteId
            self.user = user
            self.projectCode = projectCode
            self.domainName = domainName
            self.es = es
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases(fileHeader)
            self.isMock = isMock

        def getAliases(self, fileHeader):
            aliasMap = {}
            for domainName in self.domainDescriptors.keys():
                fds = self.domainDescriptors[domainName]["fieldDescriptors"]
                for fieldName in fds.keys():
                    field = fds[fieldName]
                    if "aliases" in field.keys():
                        for alias in field["aliases"]:
                            aliasMap[alias.lower()] = fieldName

            return aliasMap

        def generateRowMapFromArr(self, rowArr):
            if not rowArr:
                raise RuntimeError("empty row")

            ret = {}
            i = 0
            for token in self.fileHeader:
                if i >= len(rowArr):
                    # raise RuntimeError("not enough elements in row: " + str(i) + "/" + str(len(rowArr)))
                    continue

                val = rowArr[i]
                i += 1

                ret[token] = val

            return ret

        def processRowMap(self, rowMap):
            rowMap['siteId'] = self.siteId

            keys = list(rowMap.keys())
            for token in keys:
                # TODO: consider case sensitivity?

                val = rowMap[token]

                # append known aliases
                if token.lower() in self.aliasMap:
                    cannonicalName = self.aliasMap[token.lower()]
                else:
                    cannonicalName = token

                # allow for text on missing value
                fds = self.domainDescriptors[self.domainName]["fieldDescriptors"]
                if not val and cannonicalName in fds.keys() and 'missingValue' in fds[cannonicalName].keys():
                    val = fds[cannonicalName]['missingValue']

                # datatype conversion:
                if cannonicalName in fds.keys() and 'dataType' in fds[cannonicalName].keys() and val:
                    type =  fds[cannonicalName]['dataType']
                    try:
                        if type == 'int':
                            val = int(val)
                        elif type == 'float':
                            val = float(val)
                    except Exception:
                        raise RuntimeError(
                            "Unable to convert field: " + token + " to type: " +
                            type + " for value [" + val + "]")

                # finally append value
                rowMap[token] = val
                if token != cannonicalName:
                    rowMap[cannonicalName] = val

            # process filepath/ccc_id
            self.validateOrRegisterWithDts(rowMap)

            # append fields from other domains (denormalize)
            idx = self.domainDescriptors[self.domainName]['idx']
            domainsToAppend = []
            for dn in self.domainDescriptors:
                if dn != self.domainName and self.domainDescriptors[dn]['idx'] < idx:
                    domainsToAppend.append(dn)

            domainsToAppend.reverse()
            for dn in domainsToAppend:
                self.appendFieldsForDomain(rowMap, dn)

            # NOTE: these should always supersede the previous properties
            rowMap['siteId'] = self.siteId
            rowMap['projectCode'] = self.projectCode

            return rowMap

        def appendFieldsForDomain(self, rowMap, dn):
            if self.domainDescriptors[dn]['keyField'] in rowMap:
                key = self.generateKeyForDomain(rowMap, dn)

                try:
                    domain = self.domainDescriptors[dn]

                    hits = self.es.search(
                        index=self.getIndexNameForDomain(dn),
                        doc_type=domain['docType'],
                        ignore_unavailable=True,
                        body={
                            "size": 10000, "query": {
                                "query_string": {
                                    "query": "_id" + ":\"" + key + "\""
                                }
                            }
                        }
                    )

                    hits = hits['hits']['hits']
                    if not hits:
                        return

                    # apply data
                    hit = hits[0]
                    if ("_source" in hit.keys()):
                        rowMap.update(hit["_source"])

                except:
                    print('exception:', file=sys.stderr)
                    print(rowMap, file=sys.stderr)
                    print("index:", self.getIndexName(rowMap), file=sys.stderr)
                    print("key:", self.generateKey(rowMap), file=sys.stderr)
                    raise

        def generateKey(self, rowMap):
            return self.generateKeyForDomain(rowMap, self.domainName)

        def generateKeyForDomain(self, rowMap, domainName):
            domain = self.domainDescriptors[domainName]
            keyField = domain['keyField']

            if keyField not in rowMap:
                print('exception:', file=sys.stderr)
                print(json.dumps(rowMap), file=sys.stderr)
                raise RuntimeError("Row lacks key field: " + keyField)

            if 'useKeyFieldAsIndexKey' in domain.keys() and domain['useKeyFieldAsIndexKey']:
                return (rowMap[keyField]).lower()
            else:
                return (self.projectCode + "-" + domainName + "-" + rowMap[keyField]).lower()

        def getIndexName(self, rowMap):
            return self.getIndexNameForDomain(self.domainName)

        def getIndexNameForDomain(self, domainName):
            domain = self.domainDescriptors[domainName]
            return (self.projectCode + "-" + domain['indexPrefix']).lower()

        def pushArrToElastic(self, row):
            rowMap = self.generateRowMapFromArr(row)
            self.pushMapToElastic(rowMap)

        def pushMapToElastic(self, rowMap):
            rowMap = self.processRowMap(rowMap)

            try:
                if self.isMock:
                    print(json.dumps(rowMap))
                else:
                    self.es.index(
                        index=self.getIndexName(rowMap),
                        body=rowMap,
                        doc_type=self.domainDescriptors[self.domainName]['docType'],
                        id=self.generateKey(rowMap)
                    )
            except:
                print('exception', file=sys.stderr)
                print(rowMap, file=sys.stderr)
                print("index: " + self.getIndexName(rowMap), file=sys.stderr)
                print("key: " + self.generateKey(rowMap), file=sys.stderr)
                raise

        def validateOrRegisterWithDts(self, rowMap):
            if 'ccc_id' in rowMap.keys() and 'filepath' not in rowMap.keys() and 'url' not in rowMap.keys():
                self.validateCccId(rowMap['ccc_id'], None)
            elif 'ccc_id' in rowMap.keys() and 'filepath' in rowMap.keys():
                self.validateCccId(rowMap['ccc_id'], rowMap['filepath'])
            elif 'ccc_id' not in rowMap.keys() and 'filepath' in rowMap.keys():
                self.registerWithDts(rowMap)
            elif 'ccc_id' not in rowMap.keys() and 'url' in rowMap.keys():
                self.registerWithDts(rowMap)

        def registerWithDts(self, rowMap):
            path = rowMap['filepath'] if 'filepath' in rowMap.keys() else rowMap['url']

            if self.isMock:
                print("Assigning a mock CCC_ID", file=sys.stderr)
                rowMap['ccc_id'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
                return

            dts = ccc_client.DtsRunner()
            rowMap['ccc_id'] = dts.post(path,
                                        self.siteId,
                                        self.user)

        def validateCccId(self, ccc_id, filepath):
            if self.isMock:
                print("Skipping DTS check because this is a mock import",
                      file=sys.stderr)
                return

            dts = ccc_client.DtsRunner()
            response = dts.get(ccc_id)
            if response.status_code // 100 != 2:
                raise RuntimeError("CCC_ID not found: " + ccc_id)
            if filepath is not None:
                data = response.json()
                assert data['name'] == os.path.basename(filepath)
                assert data['path'] == os.path.dirname(filepath)
            return True
