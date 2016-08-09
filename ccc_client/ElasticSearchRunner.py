from __future__ import print_function

import csv
import json
import os
import re
import sys
import uuid

from ccc_client import DtsRunner
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
    def query(self, domainName, queries):
        if isinstance(queries, str):
            queries = [queries]
        elif isinstance(queries, list):
            pass
        else:
            raise TypeError("queries must be a str or list type")

        terms = []
        for key, val in self.__process_fields(queries).items():
            terms.append({
                "match_phrase": {
                    key: val
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
        if len(hits) > 0:
            for hit in hits:
                ret.append(hit['_source'])
        return(ret)

    # @classmethod
    def publish_resource(self, filePath, siteId, user, projectCode, workflowId,
                         mimeType, domainName, inheritFrom, properties, isMock,
                         skipDtsRegistration):

        if not self.DomainDescriptors[domainName]:
            raise RuntimeError("Unknown domain: " + domainName)

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
                raise KeyError(
                    "Unable to find existing resource with id: " + inheritFrom
                )

        # update with user supplied properties
        properties = self.__process_fields(properties)
        rowMap.update(properties)

        # NOTE: these should always supersede the properties argument
        rowMap['filepath'] = filePath
        rowMap['siteId'] = siteId
        rowMap['projectCode'] = projectCode
        rowMap['workflowId'] = workflowId
        rowMap['mimetype'] = mimeType

        rowParser = self.RowParser(rowMap.keys(), siteId, user, projectCode,
                                   'resource', self.es, self.DomainDescriptors,
                                   isMock, skipDtsRegistration)

        response = rowParser.pushMapToElastic(rowMap)
        return response

    # @classmethod
    def publish_batch(self, tsv, siteId, user, projectCode, domainName, isMock,
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
                                               projectCode,
                                               domainName, self.es,
                                               self.DomainDescriptors,
                                               isMock,
                                               skipDtsRegistration)
                else:
                    response.append(rowParser.pushArrToElastic(row))
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
        def __init__(self, fileHeader=None, siteId=None, user=None,
                     projectCode=None, domainName=None, es=None,
                     domainDescriptors=None, isMock=False,
                     skipDtsRegistration=False):

            self.fileHeader = fileHeader
            self.siteId = siteId
            self.user = user
            self.projectCode = projectCode
            self.domainName = domainName
            self.es = es
            self.domainDescriptors = domainDescriptors
            self.aliasMap = self.getAliases(fileHeader)
            self.isMock = isMock
            if isMock:
                self.skipDtsRegistration = True
            else:
                self.skipDtsRegistration = skipDtsRegistration

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
                # append known aliases
                if token.lower() in self.aliasMap:
                    cannonicalName = self.aliasMap[token.lower()]
                else:
                    cannonicalName = token

                if cannonicalName in fds.keys():
                    # allow for text on missing value
                    if val is None:
                        if 'missingValue' in fds[cannonicalName].keys():
                            val = fds[cannonicalName]['missingValue']
                    else:
                        # datatype conversion:
                        if 'dataType' in fds[cannonicalName].keys():
                            dtype = fds[cannonicalName]['dataType']
                            if dtype == 'int':
                                val = int(val)
                            elif dtype == 'float':
                                val = float(val)
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
                if token != cannonicalName:
                    rowMap[cannonicalName] = val

            # process filepath/ccc_id
            rowMap = self.validateOrRegisterWithDts(rowMap)

            # append fields from other domains (denormalize)
            domainsToAppend = list(self.domainDescriptors.keys())
            domainsToAppend.remove(self.domainName)
            for dn in domainsToAppend:
                rowMap = self.appendFieldsForDomain(rowMap, dn)

            # NOTE: these should always supersede the previous properties
            rowMap['siteId'] = self.siteId
            rowMap['projectCode'] = self.projectCode
            return rowMap

        def appendFieldsForDomain(self, rowMap, dn):
            if self.domainDescriptors[dn]['keyField'] in rowMap:
                key = self.generateKeyForDomain(rowMap, dn)
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
                if len(hits) > 0:
                    hit = hits[0]
                    rowMap.update(hit["_source"])

            return rowMap

        def generateKeyForDomain(self, rowMap, domainName):
            domain = self.domainDescriptors[domainName]
            keyField = domain['keyField']

            if keyField not in rowMap:
                print('exception:', file=sys.stderr)
                print(json.dumps(rowMap), file=sys.stderr)
                raise KeyError("Row lacks key field: " + keyField)

            if 'useKeyFieldAsIndexKey' in domain.keys():
                return (rowMap[keyField]).lower()
            else:
                domainKey = "-".join(
                    [self.projectCode, domainName, rowMap[keyField]]
                ).lower()
                return domainKey

        def getIndexNameForDomain(self, domainName):
            domain = self.domainDescriptors[domainName]
            return "-".join([self.projectCode, domain['indexPrefix']]).lower()

        def pushArrToElastic(self, row):
            rowMap = self.generateRowMapFromArr(row)
            return self.pushMapToElastic(rowMap)

        def pushMapToElastic(self, rowMap):
            rowMap = self.processRowMap(rowMap)

            if self.isMock:
                return rowMap
            else:
                response = self.es.index(
                    index=self.getIndexNameForDomain(self.domainName),
                    body=rowMap,
                    doc_type=self.domainDescriptors[self.domainName]['docType'],
                    id=self.generateKeyForDomain(rowMap, self.domainName)
                )
                return response

        def validateOrRegisterWithDts(self, rowMap):
            if 'ccc_id' in rowMap.keys():
                if 'filepath' in rowMap.keys():
                    self.validateCccId(rowMap['ccc_id'], rowMap['filepath'])
                elif 'url' in rowMap.keys():
                    self.validateCccId(rowMap['ccc_id'], rowMap['url'])
                else:
                    self.validateCccId(rowMap['ccc_id'], None)
            else:
                rowMap = self.registerWithDts(rowMap)
            return rowMap

        def registerWithDts(self, rowMap):
            if 'filepath' in rowMap.keys():
                path = rowMap['filepath']
            elif 'url' in rowMap.keys():
                path = rowMap['url']
            else:
                raise KeyError(
                    "DTS registration requires a resource path or url"
                )

            if self.skipDtsRegistration:
                print("Assigning a mock CCC_ID", file=sys.stderr)
                rowMap['ccc_id'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
            else:
                dts = DtsRunner()
                rowMap['ccc_id'] = dts.post(path,
                                            self.siteId,
                                            self.user).text
            return rowMap

        def validateCccId(self, ccc_id, filepath):
            if self.skipDtsRegistration:
                print("Skipping DTS check because this is a mock import",
                      file=sys.stderr)
            else:
                dts = DtsRunner()
                response = dts.get(ccc_id)
                if response.status_code // 100 != 2:
                    raise RuntimeError("CCC_ID not found: " + ccc_id)
                if filepath is not None:
                    data = response.json()
                    assert data['name'] == os.path.basename(filepath)
                    assert data['path'] == os.path.dirname(filepath)
            return True
