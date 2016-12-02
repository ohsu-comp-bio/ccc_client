import unittest
import tempfile
import json

from mock import patch
from ccc_client import EveMongoRunner


class TestEveMongoRunner(unittest.TestCase):
    em_client = EveMongoRunner()
    siteId = 'testSite'
    program = 'testProgram'
    project = 'testProject'
    user = 'testUser'

    mock_domain_descriptors = json.dumps(
        {
            "file": {
                "keyField": "id",
                "docType": "file",
                "indexPrefix": "file",
                "useKeyFieldAsIndexKey": True,
                "idx": 0,
                "fieldDescriptors": {
                    "id": {"aliases": ["ccc_id", "cccdid",
                                       "cccid", "ccc_did"]},
                    "ccc_filepath": {"aliases": ["ccc_filepath"]},
                    "name": {},
                    "FILEPATH": {"aliases": ["url", "filepath",
                                             "file_path"]},
                    "type": {},
                    "mimeType": {"aliases": ["mimetype"]},
                    "format": {"aliases": ["extension"]}
                }
            }
        }
    )

    mock_dd_file = tempfile.NamedTemporaryFile(delete=False)
    mock_dd_filepath = mock_dd_file.name
    mock_dd_file.write(mock_domain_descriptors.encode())
    mock_dd_file.close()

    em_mock_file = tempfile.NamedTemporaryFile(delete=False)
    em_mock_filepath = em_mock_file.name
    em_mock_file.write("id\tlocation\tformat\n".encode())
    em_mock_file.write(
        ("fakeUUID\t"+mock_dd_file.name+"\ttxt\n").encode())
    em_mock_file.close()

    def test_status(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.em_client.status()
            mock_get.assert_called_with(
                url="http://192.168.99.100:8000/v0/status"
            )

    def test_publish(self):
        # Mimic successful post
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            self.em_client.publish(
                tsv=self.em_mock_filepath,
                siteId=self.siteId,
                user=self.user,
                programCode=self.program,
                projectCode=self.project,
                domainName='file'
            )
            mock_post.assert_called_with(
                url="http://192.168.99.100:8000/v0/submission/{}/{}".format(
                    self.program, self.project),
                data=json.dumps(
                    {
                        "format": "txt",
                        "id": "fakeUUID",
                        "location": self.mock_dd_file.name,
                        "projectCode": self.project,
                        "siteId": self.siteId,
                        "type": "file"
                    },
                    sort_keys=True
                ),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

        # Check bad domain
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            with self.assertRaises(RuntimeError):
                self.em_client.publish(
                    tsv=self.em_mock_filepath,
                    siteId=self.siteId,
                    user=self.user,
                    programCode=self.program,
                    projectCode=self.project,
                    domainName='badDomain'
                )

        # Test new domain file
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            self.em_client.publish(
                tsv=self.em_mock_filepath,
                siteId=self.siteId,
                user=self.user,
                programCode=self.program,
                projectCode=self.project,
                domainName='file',
                domainFile=self.mock_dd_filepath,
            )

    def test_query(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.em_client.query(
                endpoint='files'
            )
            mock_get.assert_called_with(
                url="http://192.168.99.100:8000/v0/files",
                data=json.dumps(None),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )


if __name__ == '__main__':
    unittest.main()
