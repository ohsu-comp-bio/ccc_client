from __future__ import print_function

import json
import uuid
import re
import requests

from ccc_client.utils import parseAuthToken


class DcsRunner(object):
    """
    Send requests to the DCS
    """
    def __init__(self, host=None, port=None, authToken=None):

        if host is not None:
            self.host = re.sub("^http[s]?:",  "", host)
        else:
            self.host = "central-gateway.ccc.org"

        if port is not None:
            self.port = str(port)
        else:
            self.port = "9520"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": " ".join(["Bearer", self.authToken])
        }

        self.endpoint = "api/v1/dcs"

    def create_link(self, setId, cccId):
        endpoint = "http://{0}:{1}/{2}/resourceLink".format(self.host,
                                                            self.port,
                                                            self.endpoint)
        payload = json.dumps(self._set_relationship(setId, cccId))
        response = requests.put(endpoint,
                                data=payload,
                                headers=self.headers)
        return response

    def find_common_sets(self, ids):
        if isinstance(ids, str):
            ids = [ids]
        else:
            assert isinstance(ids, list) is True

        endpoint = "http://{0}:{1}/{2}/resourceLink/search".format(
            self.host,
            self.port,
            self.endpoint
        )
        payload = json.dumps(self._common_ids(ids))
        response = requests.post(endpoint, data=payload, headers=self.headers)
        return response

    def list_sets(self, cccId):
        endpoint = "http://{0}:{1}/{2}/resource/{3}/parents".format(
            self.host,
            self.port,
            self.endpoint,
            cccId
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def list_resources(self, setId):
        endpoint = "http://{0}:{1}/{2}/resource/{3}/children".format(
            self.host,
            self.port,
            self.endpoint,
            setId
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def delete_link(self, setId, cccId):
        endpoint = "http://{0}:{1}/{2}/resourceLink".format(self.host,
                                                            self.port,
                                                            self.endpoint)
        payload = json.dumps(self._set_relationship(setId, cccId))
        response = requests.delete(endpoint,
                                   data=payload,
                                   headers=self.headers)
        return response

    def delete_set(self, setId):
        endpoint = "http://{0}:{1}/{2}/resource/{3}".format(
            self.host,
            self.port,
            self.endpoint,
            setId
        )
        response = requests.delete(endpoint, headers=self.headers)
        return response

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
