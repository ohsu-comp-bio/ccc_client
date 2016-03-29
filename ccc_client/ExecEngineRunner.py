from __future__ import print_function

import requests


class ExecEngineRunner(object):
    """
    Send requests to the Execution Engine
    """
    def __init__(self, host=None, port=None):
        if host is not None:
            self.host = host
        else:
            self.host = "0.0.0.0"

        if port is not None:
            self.port = port
        else:
            self.port = "8000"

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
