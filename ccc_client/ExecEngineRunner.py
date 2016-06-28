from __future__ import print_function

import glob
import os
import re
import requests
import sys

from ccc_client.utils import parseAuthToken


class ExecEngineRunner(object):
    """
    Send requests to the Execution Engine
    """
    def __init__(self, host=None, port=None, authToken=None):

        if host is not None:
            self.host = re.sub("^http[s]?:",  "", host)
        else:
            self.host = "compute-0-0"

        if port is not None:
            self.port = str(port)
        else:
            self.port = "9504"

        if authToken is not None:
            self.authToken = parseAuthToken(authToken)
        else:
            self.authToken = ""

        # all other endpoints are mapped to this port
        self.secondary_port = "8000"

        self.endpoint = "api/workflows/v1"

        self.headers = {"Authorization": " ".join(["Bearer", self.authToken])}

    def submit_workflow(self, wdlSource, workflowInputs, workflowOptions):
        endpoint = "http://{0}:{1}/{2}".format(self.host,
                                               self.port,
                                               self.endpoint)

        form_data = [('wdlSource', (wdlSource, open(wdlSource, 'rb')))]
        # allow for pattern matching on workflow inputs file(s)
        for f in workflowInputs:
            file_list = glob.glob(os.path.abspath(f))
            if file_list == []:
                print("glob on", f, "did not return any files",
                      file=sys.stderr)
            else:
                form_data += [('workflowInputs', (f, open(f, 'rb'))) for f in file_list]

        response = requests.post(endpoint,
                                 files=form_data,
                                 headers=self.headers)
        return response

    def get_status(self, workflowId):
        endpoint = "http://{0}:{1}/{2}/{3}/status".format(
            self.host, self.secondary_port, self.endpoint, workflowId
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def get_metadata(self, workflowId):
        endpoint = "http://{0}:{1}/{2}/{3}/metadata".format(
            self.host, self.secondary_port, self.endpoint, workflowId
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def get_outputs(self, workflowId):
        endpoint = "http://{0}:{1}/{2}/{3}/outputs".format(
            self.host, self.secondary_port, self.endpoint, workflowId
        )
        response = requests.get(endpoint, headers=self.headers)
        return response
