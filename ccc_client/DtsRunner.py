from __future__ import print_function

import glob
import json
import os
import requests
import sys
import uuid


class DtsRunner(object):
    """
    Send requests to the DTS
    """
    def __init__(self, host=None, port=None):
        if host is not None:
            self.host = host
        else:
            self.host = "central-gateway.ccc.org"

        if port is not None:
            self.port = port
        else:
            self.port = "9510"

        self.endpoint = "api/v1/dts/file"

    def get(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        response = requests.get(
            endpoint,
            headers={'Content-Type': 'application/json'}
        )
        return response

    def delete(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        response = requests.delete(
            endpoint,
            headers={'Content-Type': 'application/json'}
        )
        return response

    def put(self, filepath, site, user, cccId):
        # TODO
        raise Exception("Not Implemented")

        endpoint = "http://{0}:{1}/{2}".format(self.host, self.port,
                                               self.endpoint)
        data = {}
        response = requests.put(
            endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        return response

    def post(self, filepath, site, user):
        # remap site name to IP
        site_map = {"central": "10.73.127.1",
                    "ohsu": "10.73.127.6",
                    "dfci": "10.73.127.18",
                    "oicr": "10.73.127.14"}

        file_list = glob.glob(os.path.abspath(filepath))
        for file_iter in file_list:
            if not os.path.isfile(file_iter):
                msg = "{0} was not found on the file system".format(file_iter)
                raise RuntimeError(msg)

            data = {}

            data['cccId'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, file_iter))
            data['name'] = os.path.basename(file_iter)
            data['size'] = os.path.getsize(file_iter)
            location = {}
            location['site'] = site_map[site]
            location['path'] = os.path.dirname(file_iter)
            location['timestampUpdated'] = os.stat(file_iter)[-2]
            location['user'] = {"name": user}
            data['location'] = [location]

            endpoint = "http://{0}:{1}/{2}".format(self.host, self.port,
                                                   self.endpoint)

            response = requests.post(
                endpoint,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code // 100 == 2:
                print("{0}    {1}".format(os.path.abspath(file_iter),
                                          data['cccId']))
            else:
                gresponse = self.get(data['cccId'])
                if gresponse.status_code // 100 == 2:
                    sys.stderr.write(
                        "[ERROR] The cccId {0} was already found in the DTS\n".format(
                            data['cccId']
                        )
                    )
                    sys.stderr.write("{0}\n".format(gresponse.text))

                sys.stderr.write(
                    "Registration with the DTS failed for: {0}\n".format(
                        os.path.abspath(file_iter)
                    )
                )
        return response
