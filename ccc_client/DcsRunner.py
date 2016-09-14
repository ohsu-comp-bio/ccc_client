from __future__ import print_function

import json
import uuid
import requests

from ccc_client.utils import parseAuthToken


class DcsRunner(object):

    def __init__(self,
                 host="central-gateway.ccc.org",
                 port=9520,
                 authToken=None):

        if isinstance(port, int):
            self.port = port
        else:
            try:
                self.port = int(port)
            except:
                raise TypeError("port could not be converted to type int")
        self.host = host

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": " ".join(["Bearer", self.authToken])
        }

        self.endpoint = self._set_url()

    def create_link(self, setId, cccId):
        payload = json.dumps(self._set_relationship(setId, cccId))
        response = requests.put(self.url,
                                data=payload,
                                headers=self.headers)
        return response

    def find_common_sets(self, ids):
        if isinstance(ids, str):
            ids = [ids]
        else:
            assert isinstance(ids, list) is True

        url = self.url + '/search'
        payload = json.dumps(self._common_ids(ids))
        response = requests.post(url, data=payload, headers=self.headers)
        return response

    def list_sets(self, cccId):
        url = self.url[:-4] + '/' + str(cccId) + '/parents'
        response = requests.get(url, headers=self.headers)
        return response

    def list_resources(self, setId):
        url = self.url[:-4] + '/' + str(setId) + '/children'
        response = requests.get(url, headers=self.headers)
        return response

    def delete_link(self, setId, cccId):
        payload = json.dumps(self._set_relationship(setId, cccId))
        response = requests.delete(self.url, data=payload, headers=self.headers)
        return response

    def delete_set(self, setId):
        url = self.url[:-4] + '/' + str(setId)
        response = requests.delete(url, headers=self.headers)
        return response

    def _set_url(self):
        self.url = "http://{0}:{1}/api/v1/dcs/resourceLink".format(
            self.host, self.port
        )

    @staticmethod
    def _set_relationship(setId, cccId):
        return {
            'parentId': setId,
            'childId': cccId
        }

    @staticmethod
    def _common_ids(ids):
        return {
            'cccIds': [str(id) for id in ids]
        }

    @staticmethod
    def _create_id(input_path=None, random=True):
        return str(uuid.uuid4()) if random else str(uuid.uuid5(uuid.noid, input_path))
