import json
import tempfile
import unittest

from mock import patch
from ccc_client import ElasticSearchRunner


class TestElasticSearchRunner(unittest.TestCase):
    es_client = ElasticSearchRunner()
    siteId = 'testSite'
    project = 'testProject'
    user = 'testUser'

    rp = es_client.RowParser(
        fileHeader=None,
        siteId=siteId,
        user=user,
        projectCode=project,
        domainName='resource',
        es=es_client.es,
        domainDescriptors=es_client.DomainDescriptors,
        isMock=False,
        skipDtsRegistration=True
    )

    mock_domain_descriptors = json.dumps(
        {
            "resource": {
                "keyField": "ccc_id",
                "docType": "resource",
                "indexPrefix": "aggregated-resource",
                "idx": 1,
                "fieldDescriptors": {
                    "ccc_id": {"aliases": ["cccdid", "cccid", "ccc_did"]},
                    "ccc_filepath": {},
                    "filename": {},
                    "filepath": {"aliases": ["file_path"]},
                    "filetype": {},
                    "extention": {}
                }
            }
        }
    )

    mock_dd_file = tempfile.NamedTemporaryFile(delete=False)
    mock_dd_file.write(mock_domain_descriptors.encode())
    mock_dd_file.close()

    es_record_to_publish = tempfile.NamedTemporaryFile(delete=False)
    es_record_filepath = es_record_to_publish.name
    es_record_to_publish.write("ccc_id\tfilepath\textension\n".encode())
    es_record_to_publish.write(("fakeUUID\t"+mock_dd_file.name+"\ttxt\n").encode())
    es_record_to_publish.close()

    def test_set_read_domainDescriptors(self):
        es = ElasticSearchRunner()
        es.setDomainDescriptors(self.mock_dd_file.name)
        self.assertEqual(es._ElasticSearchRunner__domainFile,
                         self.mock_dd_file.name)

    def test_field_processing(self):
        # dict
        res = self.es_client._ElasticSearchRunner__process_fields(
            {"foo": "bar"}
        )
        self.assertEqual(res, {"foo": "bar"})

        # list
        res = self.es_client._ElasticSearchRunner__process_fields(
            [{"foo": "bar"}]
        )
        self.assertEqual(res, {"foo": "bar"})

        # list
        res = self.es_client._ElasticSearchRunner__process_fields(
            ["foo:bar"]
        )
        self.assertEqual(res, {"foo": "bar"})

        # str
        res = self.es_client._ElasticSearchRunner__process_fields(
            "foo:bar"
        )
        self.assertEqual(res, {"foo": "bar"})

    def test_es_query(self):
        # mimic successful query of es
        with patch('elasticsearch.Elasticsearch.search') as mock_es_search:
            mock_es_search.return_value = {
                "hits": {
                    "hits": [{
                        "_source": {
                            "sample_id": "test01"
                        }
                    }]
                }
            }
            res = self.es_client.query(domainName='resource',
                                       queries=["sample_id: test01"])
            self.assertEqual(res, [{"sample_id": "test01"}])

        with self.assertRaises(TypeError):
            res = self.es_client.query(domainName='resource',
                                       queries={"sample_id": "test01"})

    def test_es_publish_resource(self):
        # test publish new resource, no inheritance
        with patch('elasticsearch.Elasticsearch.index') as mock_es_index:
            mock_es_index.return_value = {
                "_index": "resource",
                "_type": "resource",
                "_id": "1",
                "_version": 1,
                "_shards": {"total": 1,
                            "successful": 1,
                            "failed": 0},
                "created": True
            }

            res = self.es_client.publish_resource(
                filePath=self.es_record_filepath,
                siteId=self.siteId,
                user=self.user,
                projectCode=self.project,
                workflowId=None,
                mimeType="application/text",
                domainName="resource",
                inheritFrom=None,
                properties={'ccc_id': "uuid"},
                isMock=False,
                skipDtsRegistration=True
            )

            self.assertEqual(res, mock_es_index.return_value)

        # test publish new resource, with inheritance
        with patch('elasticsearch.Elasticsearch.search') as mock_es_search:
            mock_es_search.return_value = {
                "hits": {
                    "hits": [{
                        "_source": {
                            "ccc_id": "uuid1",
                            "testField": "foo"
                        }
                    }]
                }
            }
            with patch('elasticsearch.Elasticsearch.index') as mock_es_index:
                mock_es_index.return_value = {
                    "_index": "resource",
                    "_type": "resource",
                    "_id": "1",
                    "_version": 1,
                    "_shards": {"total": 1,
                                "successful": 1,
                                "failed": 0},
                    "created": True
                }

                res = self.es_client.publish_resource(
                    filePath=self.es_record_filepath,
                    siteId=self.siteId,
                    user=self.user,
                    projectCode=self.project,
                    workflowId=None,
                    mimeType="application/text",
                    domainName="resource",
                    inheritFrom="uuid1",
                    properties={'ccc_id': "uuid"},
                    isMock=False,
                    skipDtsRegistration=True
                )
                self.assertEqual(res, mock_es_index.return_value)

        # inheritFrom id is invalid
        with patch('elasticsearch.Elasticsearch.search') as mock_es_search:
            mock_es_search.return_value = {
                "hits": {
                    "hits": []
                }
            }
            with self.assertRaises(KeyError):
                res = self.es_client.publish_resource(
                    filePath=self.es_record_filepath,
                    siteId=self.siteId,
                    user=self.user,
                    projectCode=self.project,
                    workflowId=None,
                    mimeType="application/text",
                    domainName="resource",
                    inheritFrom="nonexistent-uuid",
                    properties={'ccc_id': "uuid"},
                    isMock=False,
                    skipDtsRegistration=True
                )

    def test_publish_batch(self):
        with patch('elasticsearch.Elasticsearch.index') as mock_es_index:
            mock_es_index.return_value = {
                "_index": "resource",
                "_type": "resource",
                "_id": "1",
                "_version": 1,
                "_shards": {"total": 1,
                            "successful": 1,
                            "failed": 0},
                "created": True
            }
            res = self.es_client.publish_batch(
                tsv=self.es_record_filepath,
                siteId=self.siteId,
                user=self.user,
                projectCode=self.project,
                domainName="resource",
                isMock=False,
                skipDtsRegistration=True
            )
            self.assertEqual(res, [mock_es_index.return_value])

        # test mock
        res = self.es_client.publish_batch(
                tsv=self.es_record_filepath,
                siteId=self.siteId,
                user=self.user,
                projectCode=self.project,
                domainName="resource",
                isMock=True,
                skipDtsRegistration=True
            )
        self.assertEqual(
            res,
            [{"extension": "txt",
              "projectCode": self.project,
              "siteId": self.siteId,
              "ccc_id": "fakeUUID",
              "filepath": self.mock_dd_file.name}]
        )

    def test_processRowMap(self):
        rowMap = {
            'cccdid': 'uuid',
            'file_path': '/tmp/fakepath.txt'
        }

        res = self.rp.processRowMap(rowMap)
        self.assertEqual(res['filepath'], rowMap['file_path'])
        self.assertEqual(res['ccc_id'], rowMap['cccdid'])

    def test_appendFieldsForDomain(self):
        rowMap = {
            'cccdid': 'uuid',
            'sample_id': "sample1",
            'file_path': '/tmp/fakepath.txt'
        }
        with patch('elasticsearch.Elasticsearch.search') as mock_es_search:
            mock_es_search.return_value = {
                "hits": {
                    "hits": [{
                        "_source": {
                            "sample_id": "sample1",
                            "testField": "foo"
                        }
                    }]
                }
            }
            res = self.rp.processRowMap(rowMap)
            self.assertEqual(res['filepath'], rowMap['file_path'])
            self.assertEqual(res['ccc_id'], rowMap['cccdid'])
            self.assertEqual(res['sample_id'], "sample1")
            self.assertEqual(res['testField'], "foo")

    def test_getIndexNameForDomain(self):
        self.assertEqual(
            self.rp.getIndexNameForDomain('resource'),
            self.project.lower() + '-' + 'aggregated-resource'
        )
        self.assertEqual(
            self.rp.getIndexNameForDomain('sample'),
            self.project.lower() + '-' + 'sample'
        )
        self.assertEqual(
            self.rp.getIndexNameForDomain('specimen'),
            self.project.lower() + '-' + 'specimen'
        )
        self.assertEqual(
            self.rp.getIndexNameForDomain('patient'),
            self.project.lower() + '-' + 'patient'
        )

    def test_generateKeyForDomain(self):
        rowMap = {
            'patient_id': 'PATIENT1',
            'specimen_id': 'specImen1',
            'sample_id': 'saMple1',
            'ccc_id': 'uuid',
            'filepath': '/tmp/fakepath.txt'
        }

        self.assertEqual(
            self.rp.generateKeyForDomain(rowMap, 'resource'),
            'uuid'
        )
        self.assertEqual(
            self.rp.generateKeyForDomain(rowMap, 'sample'),
            self.project.lower() + '-' + 'sample' + '-sample1'
        )
        self.assertEqual(
            self.rp.generateKeyForDomain(rowMap, 'specimen'),
            self.project.lower() + '-' + 'specimen-specimen1'
        )
        self.assertEqual(
            self.rp.generateKeyForDomain(rowMap, 'patient'),
            self.project.lower() + '-' + 'patient-patient1'
        )


if __name__ == '__main__':
    unittest.main()
