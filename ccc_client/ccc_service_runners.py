"""
CCC Service Runner Classes
"""
from __future__ import print_function


import glob
import itertools
import json
import os
import re
import requests
import sys
import uuid


class DtsRunner(object):
    """
    Send requests to the DTS
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.endpoint = "api/v1/dts/file"

    def get(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        headers = {'Content-Type': 'application/json'}
        response = requests.get(endpoint, headers=headers)
        return response

    def delete(self, cccId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                   self.endpoint, cccId)
        headers = {'Content-Type': 'application/json'}
        response = requests.delete(endpoint, headers=headers)
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
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint, data=json.dumps(data),
                                     headers=headers)

            if response.status_code // 100 == 2:
                print("{0}    {1}".format(os.path.abspath(file_iter),
                                          data['cccId']))
            else:
                sys.stderr.write(
                    "Registration with the DTS failed for:    {0}\n".format(
                        os.path.abspath(file_iter)
                    )
                )
        return response


class AppRepoRunner(object):
    """
    Send requests to the AppRepo
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.endpoint = "api/v1/tool"

    def post(self, imageBlob, imageName, imageTag):
        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)

        if imageName is None:
            imageName = re.sub("(\.tar)", "",
                               os.path.basename(imageBlob))

        form_data = {'file': open(imageBlob, 'rb'),
                     "imageName": (None, imageName),
                     "imageTag": (None, imageTag)}

        response = requests.post(endpoint, files=form_data)

        return response

    def put(self, imageId, metadata):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host,
                                                   self.port,
                                                   self.endpoint,
                                                   imageId)

        with open(metadata) as metadata_filehandle:
            loaded_metadata = json.loads(metadata_filehandle)

        if imageId is None:
            if metadata['id'] == '':
                imageId = str(uuid.uuid4())
                metadata['id'] = imageId
            else:
                imageId = metadata['id']
        else:
            if metadata['id'] == '':
                metadata['id'] = imageId

        assert imageId == metadata['id']

        headers = {'Content-Type': 'application/json'}
        response = requests.put(endpoint,
                                data=json.dumps(loaded_metadata),
                                headers=headers)
        return response

    def delete(self, imageId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host,
                                                   self.port,
                                                   self.endpoint,
                                                   imageId)
        headers = {'Content-Type': 'application/json'}
        response = requests.delete(endpoint,
                                   headers=headers)
        return response


class ExecEngineRunner(object):
    """
    Send requests to the Execution Engine
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.endpoint = "api/workflows/v1"

    def submit_workflow(self, wdlSource, workflowInputs, workflowOptions):
        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)

        form_data = {'wdlSource': open(self.wdlSource, 'rb'),
                     'workflowInputs': open(self.workflowInputs, 'rb')}

        response = requests.post(endpoint, files=form_data)
        return response

    def get_status(self):
        endpoint = "http://{0}:{1}/{2}/{3}/status".format(
            self.host, self.port, self.endpoint, self.workflowId
        )

        response = requests.get(endpoint)
        return response

    def get_metadata(self):
        endpoint = "http://{0}:{1}/{2}/{3}/metadata".format(
            self.host, self.port, self.endpoint, self.workflowId
        )

        response = requests.get(endpoint)
        return response

    def get_outputs(self):
        endpoint = "http://{0}:{1}/{2}/{3}/outputs".format(
            self.host, self.port, self.endpoint, self.workflowId
        )

        response = requests.get(endpoint)
        return response
