import json
import tempfile
import unittest

import httpretty
from ccc_client import EveMongoRunner


class TestEveMongoRunner(unittest.TestCase):
    em_client = EveMongoRunner()
    siteId = 'testSite'
    program = 'testProgram'
    project = 'testProject'
    user = 'testUser'

    rp = em_client.RowParser(
        fileHeader=None,
        siteId=siteId,
        user=user,
        programCode=program,
        projectCode=project,
        domainName='file',
        req=em_client.req,
        domainDescriptors=em_client.DomainDescriptors,
        isMock=False,
        skipDtsRegistration=True
    )

    mock_domain_descriptors = json.dumps(
        {
            "file": {
                "keyField": "id",
                "docType": "file",
                "indexPrefix": "file",
                "idx": 1,
                "fieldDescriptors": {
                    "id": {"aliases": ["cccdid", "cccid", "ccc_did", "ccc_did"]},
                    "ccc_filepath": {},
                    "name": {},
                    "location": {"aliases": ["file_path"]},
                    "type": {},
                    "format": {}
                }
            }
        }
    )

    mock_dd_file = tempfile.NamedTemporaryFile(delete=False)
    mock_dd_file.write(mock_domain_descriptors.encode())
    mock_dd_file.close()

    em_record_to_publish = tempfile.NamedTemporaryFile(delete=False)
    em_record_filepath = em_record_to_publish.name
    em_record_to_publish.write("id\tlocation\tformat\n".encode())
    em_record_to_publish.write(("fakeUUID\t"+mock_dd_file.name+"\ttxt\n").encode())
    em_record_to_publish.close()

    def test_set_read_domainDescriptors(self):
        em = EveMongoRunner()
        em.setDomainDescriptors(self.mock_dd_file.name)
        # check file reference
        self.assertEqual(em._EveMongoRunner__domainFile,
                         self.mock_dd_file.name)
        # check domain data was loaded
        self.assertEqual(em.DomainDescriptors,
                         json.loads(self.mock_domain_descriptors))

    def test_field_processing(self):
        # dict
        res = self.em_client._EveMongoRunner__process_fields(
            {"foo": "bar"}
        )
        self.assertEqual(res, {"foo": "bar"})

        # list
        res = self.em_client._EveMongoRunner__process_fields(
            [{"foo": "bar"}]
        )
        self.assertEqual(res, {"foo": "bar"})

        # list
        res = self.em_client._EveMongoRunner__process_fields(
            ["foo:bar"]
        )
        self.assertEqual(res, {"foo": "bar"})

        # str
        res = self.em_client._EveMongoRunner__process_fields(
            "foo:bar"
        )
        self.assertEqual(res, {"foo": "bar"})

    @httpretty.activate
    def test_publish_batch(self):
        mock_post = "<Response [200]>"
        httpretty.register_uri(httpretty.POST,
                               "http://192.168.99.100:8000/v0/submission/{}/{}".format(self.program, self.project),
                               body=mock_post)
        res = self.em_client.publish_batch(
            tsv=self.em_record_filepath,
            siteId=self.siteId,
            user=self.user,
            programCode=self.program,
            projectCode=self.project,
            domainName="file",
            isMock=False,
            skipDtsRegistration=True
        )
        self.assertEqual(str(res[0]), mock_post)

    def test_publish_batch_mock(self):
        res = self.em_client.publish_batch(
                tsv=self.em_record_filepath,
                siteId=self.siteId,
                user=self.user,
                programCode=self.program,
                projectCode=self.project,
                domainName="file",
                isMock=True,
                skipDtsRegistration=True
            )
        self.assertEqual(
            res,
            [{"format": "txt",
              "id": "fakeUUID",
              "location": self.mock_dd_file.name,
              "projectCode": self.project,
              "siteId": self.siteId,
              "type": "file"}]
        )

    def test_processRowMap(self):
        rowMap = {
            'cccdid': 'uuid',
            'file_path': '/tmp/fakepath.txt'
        }

        res = self.rp.processRowMap(rowMap)
        self.assertEqual(res['location'], rowMap['file_path'])
        self.assertEqual(res['id'], rowMap['cccdid'])

if __name__ == '__main__':
    unittest.main()
