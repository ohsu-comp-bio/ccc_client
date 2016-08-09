import unittest
import tempfile
import json

from mock import patch
from ccc_client import AppRepoRunner


class TestAppRepoRunner(unittest.TestCase):
    ar_client = AppRepoRunner()

    imageName = "mock"
    imageTag = "latest"
    imageId = "6dd5114a-3a6b-4ee8-9d50-bdec075998b4"
    valid_metadata_dict = {
        "description": "",
        "family": "tests",
        "approvalStatus": "review pending",
        "dockerDataVolume": "/output/",
        "input": [],
        "uploadedBy": "tester",
        "dockerImage": "docker-centos7:5000/mock",
        "version": "0.0.1",
        "scheduler": {
            "softRequirements": {
                "memory": "8000",
                "cpuCores": "1",
                "diskSpace": "8000"
            },
            "hardRequirements": {
                "memory": "8000",
                "cpuCores": "1",
                "diskSpace": "8000"
            }
        },
        "fileSystem": "hdfs",
        "owner": "tester",
        "output": [],
        "schemaVersion": "1.0",
        "id": imageId,
        "name": "mock"
    }
    valid_metadata_str = json.dumps(valid_metadata_dict)

    invalid_metadata_str = '{foo: bar}'
    invalid_metadata2_str = '{"foo": "bar"}'
    invalid_metadata3_str = '{"id": "bar"}'

    mock_img = tempfile.NamedTemporaryFile(delete=False)
    mock_img_filepath = mock_img.name
    mock_img.close()

    invalid_img_filepath = "/ZAfvcacADF/foobar.tar.gz"

    mock_metadata = tempfile.NamedTemporaryFile(delete=False)
    mock_metadata_filepath = mock_metadata.name
    mock_metadata.write(valid_metadata_str.encode())
    mock_metadata.close()

    def test_ar_post(self):
        mock_response = ""
        # mimic successful post with single input json
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = mock_response
            resp = self.ar_client.post(
                imageBlob=self.mock_img_filepath,
                imageName=self.imageName,
                imageTag="latest"
            )
            self.assertEqual(resp.text, mock_response)

        # pass path of image tarball that does not exist
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with self.assertRaises(FileNotFoundError):
                resp = self.ar_client.post(
                    imageBlob=self.invalid_img_filepath,
                    imageName=self.imageName,
                    imageTag=self.imageTag
                )

    def test_ar_put(self):
        mock_response = "OK"
        # mimic successful put metadata request w/ metadata file path
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            mock_put.return_value.text = mock_response
            resp = self.ar_client.put(
                imageId=self.imageId,
                metadata=self.mock_metadata_filepath
            )
            self.assertEqual(resp.text, mock_response)

        # mimic successful put metadata request w/ metadata json str
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            mock_put.return_value.text = mock_response
            resp = self.ar_client.put(
                imageId=self.imageId,
                metadata=self.valid_metadata_str
            )
            self.assertEqual(resp.text, mock_response)

        # mimic successful put metadata request w/ metadata dict
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            mock_put.return_value.text = mock_response
            resp = self.ar_client.put(
                imageId=self.imageId,
                metadata=self.valid_metadata_dict
            )
            self.assertEqual(resp.text, mock_response)

        # mimic unsuccessful put metadata request w/ invalid json
        with patch('requests.put') as mock_put:
            with self.assertRaises(ValueError):
                resp = self.ar_client.put(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata_str
                )

        # mimic unsuccessful put metadata request w/ valid json, invalid json
        # schema
        with patch('requests.put') as mock_put:
            with self.assertRaises(KeyError):
                resp = self.ar_client.put(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata2_str
                )

        # mimic unsuccessful put metadata request where imageId doesn't match
        # metadata imageId field
        with patch('requests.put') as mock_put:
            with self.assertRaises(AssertionError):
                resp = self.ar_client.put(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata3_str
                )

    def test_ar_get(self):
        mock_response = self.valid_metadata_str
        # mimic successful get request:
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = mock_response
            # by id
            resp = self.ar_client.get(
                imageId=self.imageId,
                imageName=None
            )
            self.assertEqual(resp.text, mock_response)
            # by name
            resp = self.ar_client.get(
                imageId=None,
                imageName=self.imageName
            )
            self.assertEqual(resp.text, mock_response)

    def test_ar_delete(self):
        mock_response = "OK"
        # mimic successful get request:
        with patch('requests.delete') as mock_delete:
            mock_delete.return_value.status_code = 201
            mock_delete.return_value.text = mock_response
            resp = self.ar_client.delete(
                imageId=self.imageId,
            )
            self.assertEqual(resp.text, mock_response)


if __name__ == '__main__':
    unittest.main()
