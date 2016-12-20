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
            self.host = re.sub("^http[s]?://",  "", host)
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

    def put(self, cccId, filepath, sites, user=None):
        filepath = os.path.abspath(filepath)
        sites = self._process_sites(sites)
        user = self._process_user(user)

        # get current record
        resp = self.get(cccId)
        data = json.loads(resp.text)

        # some checks for safety
        try:
            assert data['cccId'] == self._generate_cccId(filepath)
        except:
            print("[WARNING] the cccId was not generated via the",
                  "standard method provided by this library",
                  file=sys.stderr)

        try:
            assert data['name'] == os.path.basename(filepath)
            assert data['size'] == os.path.getsize(filepath)
        except:
            print("[ERROR] the name and/or size of this file doesn't",
                  "match the current record",
                  file=sys.stderr)
            raise ValueError

        # update record
        locations = []
        location = {}
        for site in sites:
            if not any(site in s for s in data['location']):
                location = {}
            else:
                i = next(
                    (i for i, d in enumerate(data['location']) if site in d),
                    None
                )
                location = data['location'][i]

            location['site'] = self._map_site_to_ip(site)
            location['path'] = os.path.dirname(filepath)
            location['timestampUpdated'] = os.stat(filepath)[-2]
            location['user'] = {"name": user}
            locations.append(location)

        data['location'] = locations
        endpoint = "http://{0}:{1}/{2}".format(self.host, self.port,
                                               self.endpoint)
        response = requests.put(
            endpoint,
            data=json.dumps(data, sort_keys=True),
            headers=self.headers
        )
        return response

    def post(self, filepath, sites, user=None, cccId=None):
        filepath = os.path.abspath(filepath)
        sites = self._process_sites(sites)
        user = self._process_user(user)

        data = {}
        if cccId is not None:
            if self._check_cccId(cccId):
                print("[ERROR] The cccId", cccId,
                      "was already present in the DTS",
                      file=sys.stderr)
                raise ValueError
            else:
                data['cccId'] = cccId
        else:
            data['cccId'] = self._generate_cccId(filepath)

        data['name'] = os.path.basename(filepath)
        data['size'] = os.path.getsize(filepath)

        locations = []
        for site in sites:
            location = {}
            location['site'] = self._map_site_to_ip(site)
            location['path'] = os.path.dirname(filepath)
            location['timestampUpdated'] = os.stat(filepath)[-2]
            location['user'] = {"name": user}
            locations.append(location)

        data['location'] = locations

        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)
        response = requests.post(
            endpoint,
            data=json.dumps(data, sort_keys=True),
            headers=self.headers
        )

        if response.status_code // 100 != 2:
            print("[ERROR] Registration with the DTS failed for:",
                  filepath,
                  file=sys.stderr)
            if self._check_cccId(data['cccId']):
                print("[ERROR] The cccId", data['cccId'],
                      "was already present in the DTS",
                      file=sys.stderr)
                raise ValueError
        return response

    def query(self, filepath, site):
        name = os.path.basename(filepath)
        path = os.path.dirname(filepath)
        terms = [
            "name={0}".format(name),
            "path={0}".format(path),
            "site={0}".format(self._map_site_to_ip(site))
        ]
        query_string = "&".join(terms)
        endpoint = "http://{0}:{1}/{2}/?{3}".format(
            self.host, self.port, self.endpoint, query_string
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def infer_cccId(self, filepath, uuid_strategy="SHA-1"):
        return self._generate_cccId(filepath, uuid_strategy)

    def _check_cccId(self, cccId):
        cccId_check_response = self.get(cccId)
        if cccId_check_response.status_code // 100 == 2:
            return True
        else:
            return False

    def _generate_cccId(self, filepath, uuid_strategy="SHA-1"):
        filepath = os.path.abspath(filepath)
        if uuid_strategy.upper() == "RANDOM":
            cccId = str(uuid.uuid4())
        elif uuid_strategy.upper() == "MD5":
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

    def _map_site_to_ip(self, site):
        site_map = {"central": "http://10.73.127.1",
                    "ohsu": "http://10.73.127.6",
                    "dfci": "http://10.73.127.18",
                    "oicr": "http://10.73.127.14"}
        try:
            url = site_map[site]
            return url
        except KeyError:
            print("[ERROR] valid values for 'site' are:",
                  "central, ohsu, oicr, and dfci",
                  file=sys.stderr)
            raise KeyError

    def _process_sites(self, sites):
        if isinstance(sites, list):
            pass
        elif isinstance(sites, str):
            sites = [sites]
        else:
            print("[ERROR] 'sites' must be a string or list",
                  file=sys.stderr)
            raise TypeError
        return sites

    def _process_user(self, user):
        if user is None:
            user = os.environ['USER']
        return user
