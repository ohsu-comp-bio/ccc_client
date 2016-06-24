from __future__ import print_function

import json
import os
import re
import requests
import sys
import uuid

from ccc_client.utils import parseAuthToken


class DtsRunner(object):
    """
    Send requests to the DTS
    """
    def __init__(self, host=None, port=None, authToken=None):

        if host is not None:
            self.host = re.sub("^http[s]?:",  "", host)
        else:
            self.host = "central-gateway.ccc.org"

        if port is not None:
            self.port = str(port)
        else:
            self.port = "9510"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.headers = {
            'Content-Type': 'application/json',
            "Authorization": " ".join(["Bearer", self.authToken])
        }

        self.endpoint = "api/v1/dts/file"

        self.site_map = {"central": "http://10.73.127.1",
                         "ohsu": "http://10.73.127.6",
                         "dfci": "http://10.73.127.18",
                         "oicr": "http://10.73.127.14"}

    def get(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        response = requests.get(
            endpoint,
            headers=self.headers
        )
        return response

    def delete(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        response = requests.delete(
            endpoint,
            headers=self.headers
        )
        return response

    def put(self, cccId, filepath=None, site=None, user=None):
        if all(v is None for v in [filepath, site, user]):
            print("At least one of: filepath, site, user must not be None",
                  file=sys.stderr)
            raise

        resp = self.get(cccId)
        data = resp.json()

        if filepath is not None:
            filepath = os.path.abspath(filepath)
            assert data['cccId'] == str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                   filepath))

            data['name'] = os.path.basename(filepath)
            data['size'] = os.path.getsize(filepath)
            data['location']['path'] = os.path.dirname(filepath)
            data['location']['timestampUpdated'] = os.stat(filepath)[-2]

        if site is not None:
            data['location']['site'] = self.site_map[site]

        if user is not None:
            data['location']['user'] = {"name": user}

        endpoint = "http://{0}:{1}/{2}".format(self.host, self.port,
                                               self.endpoint)
        response = requests.put(
            endpoint,
            data=json.dumps(data),
            headers=self.headers
        )

        if response.status_code // 100 != 2:
            print("Update of DTS entry:", data['cccId'], "failed",
                  file=sys.stderr)

        return response

    def post(self, filepath, site, user, cccId=None):
        filepath = os.path.abspath(filepath)
        data = {}

        if cccId is not None:
            cccId_check_response = self.get(cccId)
            if cccId_check_response.status_code // 100 == 2:
                print("[ERROR] The cccId", cccId,
                      "was already found in the DTS",
                      file=sys.stderr)
                print(cccId_check_response.text, file=sys.stderr)
                raise
            else:
                data['cccId'] = cccId
        else:
            data['cccId'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, filepath))

        data['name'] = os.path.basename(filepath)
        data['size'] = os.path.getsize(filepath)
        location = {}
        location['site'] = self.site_map[site]
        location['path'] = os.path.dirname(filepath)
        location['timestampUpdated'] = os.stat(filepath)[-2]
        location['user'] = {"name": user}
        data['location'] = [location]

        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)

        response = requests.post(
            endpoint,
            data=json.dumps(data),
            headers=self.headers
        )

        if response.status_code // 100 != 2:
            print("Registration with the DTS failed for:",
                  filepath,
                  file=sys.stderr)
            gresponse = self.get(data['cccId'])
            if gresponse.status_code // 100 == 2:
                print("[ERROR] The cccId", data['cccId'],
                      "was already found in the DTS",
                      file=sys.stderr)
                print(gresponse.text, file=sys.stderr)
        return response

    def infer_cccId(self, filepath, uuid_strategy="SHA-1"):
        filepath = os.path.abspath(filepath)
        if uuid_strategy.upper() == "MD5":
            cccId = str(uuid.uuid3(uuid.NAMESPACE_DNS, filepath))
        elif uuid_strategy.upper() == "SHA-1":
            cccId = str(uuid.uuid5(uuid.NAMESPACE_DNS, filepath))
        else:
            raise RuntimeError(
                "uuid hashing strategy: {0} not supported\n".format(
                    uuid_strategy
                )
            )
        return cccId
