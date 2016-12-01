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
    valid_metadata_str = json.dumps(valid_metadata_dict, sort_keys=True)

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

    def test_ar_upload_image(self):
        # mimic successful post with single input json
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            self.ar_client.upload_image(
                imageBlob=self.mock_img_filepath,
                imageName=self.imageName,
                imageTag="latest"
            )
            assert mock_post.called

        # pass path of image tarball that does not exist
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with self.assertRaises(IOError):
                self.ar_client.upload_image(
                    imageBlob=self.invalid_img_filepath,
                    imageName=self.imageName,
                    imageTag=self.imageTag
                )

    def test_ar_create_or_update_metadata(self):
        url = "http://docker-centos7:8082/api/v1/tool/{0}"

        # mimic successful put metadata request w/ metadata file path
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            self.ar_client._AppRepoRunner__create_or_update_metadata(
                imageId=self.imageId,
                metadata=self.mock_metadata_filepath
            )
            mock_put.assert_called_once_with(
                url.format(self.imageId),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                },
                data=self.valid_metadata_str
            )

        # mimic successful put metadata request w/ metadata json str
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            self.ar_client._AppRepoRunner__create_or_update_metadata(
                imageId=self.imageId,
                metadata=self.valid_metadata_str
            )
            mock_put.assert_called_once_with(
                url.format(self.imageId),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                },
                data=self.valid_metadata_str
            )

        # mimic successful put metadata request w/ metadata dict
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            self.ar_client._AppRepoRunner__create_or_update_metadata(
                imageId=self.imageId,
                metadata=self.valid_metadata_dict
            )
            mock_put.assert_called_once_with(
                url.format(self.imageId),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                },
                data=self.valid_metadata_str
            )

        # mimic unsuccessful put metadata request w/ invalid json
        with patch('requests.put') as mock_put:
            with self.assertRaises(ValueError):
                self.ar_client._AppRepoRunner__create_or_update_metadata(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata_str
                )

        # mimic unsuccessful put metadata request w/ valid json, invalid json
        # schema
        with patch('requests.put') as mock_put:
            with self.assertRaises(KeyError):
                self.ar_client._AppRepoRunner__create_or_update_metadata(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata2_str
                )

        # mimic unsuccessful put metadata request where imageId doesn't match
        # metadata imageId field
        with patch('requests.put') as mock_put:
            with self.assertRaises(AssertionError):
                self.ar_client._AppRepoRunner__create_or_update_metadata(
                    imageId=self.imageId,
                    metadata=self.invalid_metadata3_str
                )

    def test_ar_upload_metadata(self):
        # try to overwrite existing metadata
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            with self.assertRaises(ValueError):
                self.ar_client.upload_metadata(
                    imageId=self.imageId,
                    metadata=self.mock_metadata_filepath
                )

    def test_ar_get_metadata(self):
        # mimic successful get request:
        # by image id
        with patch('requests.get') as mock_get:
            url = "http://docker-centos7:8082/api/v1/tool/{0}"
            mock_get.return_value.status_code = 200
            self.ar_client.get_metadata(
                image_id_or_name=self.imageId,
            )
            mock_get.assert_called_once_with(
                url.format(self.imageId),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                }
            )

        # by image name
        with patch('requests.get') as mock_get:
            url = "http://docker-centos7:8082/api/v1/tool/{0}/data"
            mock_get.return_value.status_code = 500
            self.ar_client.get_metadata(
                image_id_or_name=self.imageName,
            )
            mock_get.assert_called_with(
                url.format(self.imageName),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                }
            )

    def test_ar_delete_metadata(self):
        # mimic delete request:
        with patch('requests.delete') as mock_delete:
            self.ar_client.delete_metadata(
                imageId=self.imageId,
            )
            url = "http://docker-centos7:8082/api/v1/tool/{0}"
            mock_delete.assert_called_with(
                url.format(self.imageId),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer '
                }
            )

    def test_ar_list_tools(self):
        # mimic list_tools request:
        with patch('requests.get') as mock_get:
            self.ar_client.list_tools()
            mock_get.assert_called_with(
                "http://docker-centos7:5000/v2/_catalog",
            )


if __name__ == '__main__':
    unittest.main()
