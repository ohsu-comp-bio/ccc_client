import unittest
import tempfile
import json
import os
import uuid

from mock import patch
from ccc_client import DcsRunner


class TestDcsRunner(unittest.TestCase):
    dcs_client = DcsRunner()

    mock_setId = str(uuid.uuid4())
    mock_cccId = str(uuid.uuid4())

    def test_create_link(self):
        # mimic successful link creation
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 201
            self.dcs_client.create_link(
                parentId=self.mock_setId,
                childId=self.mock_cccId
            )
            mock_put.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resourceLink",
                data=json.dumps(
                    {"parentId": self.mock_setId, "childId": self.mock_cccId}
                ),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

    def test_common_parents(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 201
            self.dcs_client.common_parents(
                ids=self.mock_cccId
            )
            mock_post.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resourceLink/search",
                data=json.dumps({"cccIds": [self.mock_cccId]}),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

    def test_all_parents(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 201
            self.dcs_client.all_parents(
                childId=self.mock_cccId
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resource/{0}/parents".format(self.mock_cccId),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

    def test_all_children(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 201
            self.dcs_client.all_children(
                parentId=self.mock_setId
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resource/{0}/children".format(self.mock_setId),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

    def test_delete_link(self):
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value.status_code = 201
            self.dcs_client.delete_link(
                parentId=self.mock_setId,
                childId=self.mock_cccId
            )
            mock_delete.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resourceLink",
                data=json.dumps(
                    {"parentId": self.mock_setId, "childId": self.mock_cccId}
                ),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )

    def test_delete_set(self):
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value.status_code = 201
            self.dcs_client.delete_set(
                parentId=self.mock_setId
            )
            mock_delete.assert_called_with(
                "http://central-gateway.ccc.org:9520/api/v1/dcs/resource/{0}".format(self.mock_setId),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer "}
            )


if __name__ == "__main__":
    unittest.main()
