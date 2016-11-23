from __future__ import print_function

import json
import os
import re
import sys
import requests
import uuid
from ccc_client.utils import parseAuthToken


class AppRepoRunner(object):
    """
    Send requests to the AppRepo
    """
    def __init__(self, host=None, port=None, authToken=None):

        if host is not None:
            self.host = re.sub("^http[s]?:",  "", host)
        else:
            self.host = "docker-centos7"

        if port is not None:
            self.port = str(port)
        else:
            self.port = "8082"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        self.endpoint = "api/v1/tool"

        self.headers = {
            "Authorization": " ".join(["Bearer", self.authToken])
        }

    def upload_image(self, imageBlob, imageName, imageTag):
        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)

        if imageName is None:
            imageName = re.sub("(\.tar)", "",
                               os.path.basename(imageBlob))

        if imageTag is None:
            imageTag = "latest"

        form_data = {'file': open(imageBlob, 'rb'),
                     "imageName": (None, imageName),
                     "imageTag": (None, imageTag)}

        headers = self.__setup_call_headers("post")
        response = requests.post(endpoint,
                                 files=form_data,
                                 headers=headers)
        return response

    def upload_metadata(self, imageId, metadata):
        response = self.get_metadata(imageId)
        if response.status_code // 100 == 2:
            print("[ERROR] An entry with this id already exists in the database", file=sys.stderr)
            print(response.text, file=sys.stderr)
            raise ValueError
        else:
            self.__create_or_update_metadata(imageId, metadata)

    def update_metadata(self, imageId, metadata):
        self.__create_or_update_metadata(imageId, metadata)

    def __create_or_update_metadata(self, imageId, metadata):
        if isinstance(metadata, str):
            if os.path.isfile(metadata):
                with open(metadata) as metadata_filehandle:
                    metadata = metadata_filehandle.read()
            else:
                pass
            loaded_metadata = json.loads(metadata.replace("'", '"'))
        elif isinstance(metadata, dict):
            loaded_metadata = metadata
        else:
            raise TypeError("metadata must be a python dict or str")

        if imageId is None:
            if loaded_metadata['id'] == '':
                imageId = str(uuid.uuid4())
                loaded_metadata['id'] = imageId
            else:
                imageId = loaded_metadata['id']
        else:
            if loaded_metadata['id'] == '':
                loaded_metadata['id'] = imageId
            else:
                assert loaded_metadata['id'] == imageId

        headers = self.__setup_call_headers("put")
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host,
                                                   self.port,
                                                   self.endpoint,
                                                   imageId)
        response = requests.put(
            endpoint,
            data=json.dumps(loaded_metadata, sort_keys=True),
            headers=headers
        )
        return response

    def get_metadata(self, image_id_or_name):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host,
                                                   self.port,
                                                   self.endpoint,
                                                   image_id_or_name)
        headers = self.__setup_call_headers("get")
        response = requests.get(
            endpoint,
            headers=headers
        )
        if response.status_code // 100 != 2:
            endpoint = "http://{0}:{1}/{2}/{3}/data".format(self.host,
                                                            self.port,
                                                            self.endpoint,
                                                            image_id_or_name)
            headers = self.__setup_call_headers("get")
            response = requests.get(
                endpoint,
                headers=headers
            )
        return response

    def delete_metadata(self, imageId):
        endpoint = "http://{0}:{1}/{2}/{3}".format(self.host,
                                                   self.port,
                                                   self.endpoint,
                                                   imageId)
        headers = self.__setup_call_headers("delete")
        response = requests.delete(
            endpoint,
            headers=headers
        )
        return response

    def list_tools(self):
        endpoint = "http://{0}:5000/v2/_catalog".format(self.host)
        response = requests.get(
            endpoint
        )
        return response

    def __setup_call_headers(self, method):
        call_header = self.headers.copy()
        if method == "post":
            call_header.update({'Content-Type': 'multipart/form-data'})
        else:
            call_header.update({'Content-Type': 'application/json'})
        return call_header
