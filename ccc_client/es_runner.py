"""
Elastic Search Service Runner
"""
import csv
import sys
import json
import os
from elasticsearch import Elasticsearch


class ElasticSearchRunner(object):
    def __init__(self, args):
        if args.host is not None:
            self.host = args.host
        else:
            # TODO: figure out what the correct defualt should be
            self.host = "0.0.0.0"

        if args.port is not None:
            self.port = args.port
        else:
            self.port = "9200"

        self.token = args.token
        self.readDomainDescriptors()
        self.es = Elasticsearch(hosts="{0}:{1}".format(self.host, self.port))

    # Note: this creates the opportunity to allow externally provided field
    # definitions, or potentially a different schema at runtime
    def readDomainDescriptors(self):
        ddFile = os.path.dirname(os.path.realpath(__file__))
        ddFile = ddFile + "/domains.json"
        with open(ddFile) as json_data:
            self.DomainDescriptors = json.load(json_data)

            json_data.close()

    # @classmethod
    def query(self, domainName, queries, output):
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

        if (output):
            with open(output, 'w') as outfile:
                outfile.write(json.dumps(ret))
        else:
            print(ret)

    # @classmethod
    def publish_resource(self, filePath, ccc_did, siteId, projectName,
                         workflowId, fileType, domainName, inheritFrom,
                         properties):
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
                                    "ccc_did": inheritFrom
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
                raise RuntimeError("Unable to find existing resource with id: " + inheritFrom)

        rowMap['ccc_did'] = ccc_did
        rowMap['filePath'] = filePath
        rowMap['siteId'] = siteId
        rowMap['projectName'] = projectName
        rowMap['workflowId'] = workflowId
        rowMap['fileType'] = fileType

        for prop in properties:
            tokens = prop.split(":")
            rowMap[tokens[0]] = tokens[1]

        rowParser = self.RowParser(rowMap.keys(), siteId, projectName,
                                   'resource', self.es, self.DomainDescriptors)
        rowParser.pushMapToElastic(rowMap)

    # @classmethod
    def print_domain(self, domainName):
        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

        domain = self.DomainDescriptors[domainName]
        print(domain)

    # @classmethod
    def publish_batch(self, tsv, siteId, projectName, domainName):
        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

        self._processRows(tsv, siteId, projectName, domainName)

    def _processRows(self, tsv, siteId, projectName, domainName):
        read_mode = 'rb' if sys.version_info[0] < 3 else 'r'
        i = 0
        with open(tsv, mode=read_mode) as infile:
            reader = csv.reader(infile, delimiter='\t')
            for row in reader:
                if i == 0:
                    rowParser = self.RowParser(row, siteId, projectName,
                                               domainName, self.es,
                                               self.DomainDescriptors)
                else:
                    rowParser.pushArrToElastic(row)

                i =+ 1

    # @classmethod
    def merge(self):
        raise NotImplementedError()


    # Responsible for inspecting the header and normalizing/augmenting field names
    class RowParser(object):
        # array of raw data
        fileHeader = None
        siteId = None
        aliasMap = {}
        domainName = None
        es = None
        domainDescriptors = None

        def __init__(self, fileHeader=None, siteId=None, projectName=None,
                     domainName=None, es=None, domainDescriptors=None):
            self.fileHeader = fileHeader
            self.siteId = siteId
            self.projectName = projectName
            self.domainName = domainName
            self.es = es
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases(fileHeader)

        def getAliases(self, fileHeader):
            aliasMap = {}
            for domainName in self.domainDescriptors.keys():
                fds = self.domainDescriptors[domainName]["fieldDescriptors"]
                for fieldName in fds.keys():
                    field = fds[fieldName]
                    if "aliases" in field.keys():
                        for alias in field["aliases"]:
                            if alias in fileHeader:
                                aliasMap[alias] = fieldName

            return aliasMap

        def generateRowMap(self, rowArr):
            rowMap = {'siteId': self.siteId}

            if not rowArr:
                raise RuntimeError("empty row")

            i = 0
            for token in self.fileHeader:
                if i >= len(rowArr):
                    # raise RuntimeError("not enough elements in row: " + str(i) + "/" + str(len(rowArr)))
                    continue

                val = rowArr[i]
                i += 1

                # append known aliases
                if token in self.aliasMap:
                    cannonicalName = self.aliasMap[token]
                else:
                    cannonicalName = token

                # allow for text on missing value
                fds = self.domainDescriptors[self.domainName]["fieldDescriptors"]
                if not val and cannonicalName in fds.keys() and 'missingValue' in fds[cannonicalName].keys():
                    val = fds[cannonicalName]['missingValue']

                # datatype conversion:
                if cannonicalName in fds.keys() and 'dataType' in fds[cannonicalName].keys():
                    type =  fds[cannonicalName]['dataType']
                    try:
                        if type == 'int':
                            val = int(val)
                        elif type == 'float':
                            val = float(val)
                    except Exception:
                        raise RuntimeError("Unable to convert field: " +
                                           token + " to type: " + type +
                                           " for value [" + val + "]")

                # finally append value
                rowMap[token] = val
                if token != cannonicalName:
                    rowMap[cannonicalName] = val

            # append fields from other domains (denormalize)
            idx = self.domainDescriptors[self.domainName]['idx']
            domainsToAppend = []
            for dn in self.domainDescriptors:
                if dn != self.domainName and self.domainDescriptors[dn]['idx'] < idx:
                    domainsToAppend.append(dn)

            domainsToAppend.reverse()
            for dn in domainsToAppend:
                self.appendFieldsForDomain(rowMap, dn)

            return rowMap

        def appendFieldsForDomain(self, rowMap, dn):
            if self.domainDescriptors[dn]['keyField'] in rowMap:
                key = self.generateKeyForDomain(rowMap, dn)

                try:
                    domain = self.domainDescriptors[dn]

                    hits = self.es.search(
                        index=self.getIndexNameForDomain(rowMap, dn),
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
                    print(rowMap)
                    print("index: " + self.getIndexName(rowMap))
                    print("key: " + self.generateKey(rowMap))
                    raise

        def generateKey(self, rowMap):
            return self.generateKeyForDomain(rowMap, self.domainName)

        def generateKeyForDomain(self, rowMap, domainName):
            keyField = self.domainDescriptors[domainName]['keyField']

            if keyField not in rowMap:
                raise RuntimeError("Row lacks key field: " + keyField)

            return (self.projectName + "-" + domainName + "-" +
                    rowMap[keyField]).lower()

        def getIndexName(self, rowMap):
            return self.getIndexNameForDomain(rowMap, self.domainName)

        def getIndexNameForDomain(self, rowMap, domainName):
            return (self.projectName + "-" + domainName).lower()

        def pushArrToElastic(self, row):
            rowMap = self.generateRowMap(row)
            self.pushMapToElastic(rowMap)

        def pushMapToElastic(self, rowMap):
            try:
                self.es.index(
                    index=self.getIndexName(rowMap),
                    body=rowMap,
                    doc_type=self.domainDescriptors[self.domainName]['docType'],
                    id=self.generateKey(rowMap)
                )
            except:
                print(rowMap)
                print("index: " + self.getIndexName(rowMap))
                print("key: " + self.generateKey(rowMap))
                raise
