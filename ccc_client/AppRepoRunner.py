from __future__ import print_function

import json
import os
import re
import requests
import uuid


class AppRepoRunner(object):
    """
    Send requests to the AppRepo
    """
    def __init__(self, host=None, port=None):
        if host is not None:
            self.host = host
        else:
            self.host = "docker-centos7"

        if port is not None:
            self.port = port
        else:
            self.port = "8082"

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

        if os.path.isfile(metadata):
            with open(metadata) as metadata_filehandle:
                loaded_metadata = json.loads(metadata_filehandle.read())
        else:
            loaded_metadata = json.loads(metadata)

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
