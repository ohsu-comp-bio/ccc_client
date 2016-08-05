import unittest
import tempfile
import json
import os
import uuid

from mock import patch
from ccc_client import DtsRunner


class TestDtsRunner(unittest.TestCase):
    dts_client = DtsRunner()

    mock_file = tempfile.NamedTemporaryFile(delete=False)
    mock_filepath = mock_file.name
    ccc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, mock_filepath))

    site = "ohsu"
    sites = ["ohsu", "central"]
    invalid_site = "test"
    user = "dts_tester"

    def test_dts_post(self):
        # mimick successful post
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = self.ccc_id
            resp = self.dts_client.post(
                filepath=self.mock_filepath,
                sites=self.site,
                user=self.user,
                cccId=None
            )

            self.assertEqual(resp.text, self.ccc_id)

        # mimick file already being registered
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 201
                with self.assertRaises(ValueError):
                    resp = self.dts_client.post(
                        filepath=self.mock_filepath,
                        sites=self.site,
                        user=self.user,
                        cccId=None
                    )

        # mimick successful post w/ user provided ccc id
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = self.ccc_id
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 500
                resp = self.dts_client.post(
                    filepath=self.mock_filepath,
                    sites=self.site,
                    user=self.user,
                    cccId=self.ccc_id
                )
                self.assertEqual(resp.text, self.ccc_id)

        # mimick failed post w/ user provided ccc id
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = self.ccc_id
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 201
                with self.assertRaises(ValueError):
                    resp = self.dts_client.post(
                        filepath=self.mock_filepath,
                        sites=self.site,
                        user=self.user,
                        cccId=self.ccc_id
                    )

    def test_dts_update(self):
        # mimick successful update
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            mock_put.return_value.text = "OK"
            with patch('requests.get') as mock_get:
                mock_get.return_value.status_code = 201
                mock_get.return_value.text = json.dumps(
                    {
                        "cccId": self.ccc_id,
                        "name": os.path.basename(self.mock_filepath),
                        "size": os.path.getsize(self.mock_filepath),
                        "location": [{
                            "site": "http://10.73.127.14",
                            "path": os.path.dirname(self.mock_filepath),
                            "timestampUpdated": 1468263436,
                            "user": {
                                "name": "dts_tester"
                            }
                        }]
                    }
                )
                resp = self.dts_client.put(
                    filepath=self.mock_filepath,
                    sites=self.sites,
                    user=self.user,
                    cccId=self.ccc_id
                )
                self.assertEqual(resp.text, "OK")

        # mimick update attempt where filepath doesn't match expected cccId
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = json.dumps(
                {
                    "cccId": self.ccc_id,
                    "name": os.path.basename(self.mock_filepath),
                    "size": os.path.getsize(self.mock_filepath),
                    "location": [{
                        "site": "http://10.73.127.14",
                        "path": os.path.dirname(self.mock_filepath),
                        "timestampUpdated": 1468263436,
                        "user": {
                            "name": "dts_tester"
                        }
                    }]
                }
            )
            with self.assertRaises(ValueError):
                resp = self.dts_client.put(
                    filepath="/tmp/foobar",
                    sites=self.sites,
                    user=self.user,
                    cccId=self.ccc_id
                )

    def test_cccId_generation(self):
        self.assertEqual(
            self.dts_client.infer_cccId(filepath=self.mock_filepath, uuid_strategy="SHA-1"),
            str(uuid.uuid5(uuid.NAMESPACE_DNS, self.mock_filepath))
        )
        self.assertEqual(
            self.dts_client.infer_cccId(filepath=self.mock_filepath, uuid_strategy="MD5"),
            str(uuid.uuid3(uuid.NAMESPACE_DNS, self.mock_filepath))
        )
        self.assertNotEqual(
            self.dts_client.infer_cccId(filepath=self.mock_filepath, uuid_strategy="RANDOM"),
            str(uuid.uuid5(uuid.NAMESPACE_DNS, self.mock_filepath))
        )
        self.assertNotEqual(
            self.dts_client.infer_cccId(filepath=self.mock_filepath, uuid_strategy="RANDOM"),
            str(uuid.uuid3(uuid.NAMESPACE_DNS, self.mock_filepath))
        )

    def test_site_mapping(self):
        self.assertEqual(
            self.dts_client._map_site_to_ip("central"),
            "http://10.73.127.1"
        )
        self.assertEqual(
            self.dts_client._map_site_to_ip("ohsu"),
            "http://10.73.127.6"
        )
        self.assertEqual(
            self.dts_client._map_site_to_ip("oicr"),
            "http://10.73.127.14"
        )
        self.assertEqual(
            self.dts_client._map_site_to_ip("dfci"),
            "http://10.73.127.18"
        )

    # the below tests don't really do anything...
    def test_dts_get(self):
        mock_dts_entry = json.dumps(
            {
                "cccId": self.ccc_id,
                "name": os.path.basename(self.mock_filepath),
                "size": os.path.getsize(self.mock_filepath),
                "location": [{
                    "site": "http://10.73.127.14",
                    "path": os.path.dirname(self.mock_filepath),
                    "timestampUpdated": 1468263436,
                    "user": {
                        "name": "dts_tester"
                    }
                }]
            }
        )

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = mock_dts_entry
            resp = self.dts_client.get(
                cccId=self.ccc_id
            )
            self.assertEqual(resp.text, mock_dts_entry)

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 500
            resp = self.dts_client.get(
                cccId=self.ccc_id
            )
            self.assertEqual(resp.status_code, 500)

    def test_dts_delete(self):
        with patch('requests.delete') as mock_delete:
            mock_delete.return_value.status_code = 201
            mock_delete.return_value.text = "OK"
            resp = self.dts_client.delete(
                cccId=self.ccc_id
            )
            self.assertEqual(resp.text, "OK")


if __name__ == '__main__':
    unittest.main()
