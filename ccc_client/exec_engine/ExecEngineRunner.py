from __future__ import print_function

import glob
import iso8601
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
            self.host = re.sub("^http[s]?://",  "", host)
        else:
            self.host = "central-gateway.ccc.org"

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
        if isinstance(workflowInputs, str):
            workflowInputs = [workflowInputs]
        elif isinstance(workflowInputs, list):
            assert all(isinstance(n, str) for n in workflowInputs)
        else:
            raise TypeError("WorkflowInputs must be str or list type")
        for f in workflowInputs:
            file_list = glob.glob(os.path.abspath(f))
            if file_list == []:
                print("glob on", f, "did not return any files",
                      file=sys.stderr)
            else:
                for f in file_list:
                    fh = open(f, 'rb')
                    item = 'workflowInputs', (f, fh)
                    form_data.append(item)

        response = requests.post(endpoint,
                                 files=form_data,
                                 headers=self.headers)
        return response

    def query(self, query_terms):
        """
        GET version of cromwell query
        """
        valid_terms = [
            "name", "id", "status", "start", "end", "page", "pagesize"
        ]
        valid_statuses = [
            "Submitted", "Running", "Aborted", "Failed", "Succeeded"
        ]
        terms = []
        for query in query_terms:
            key, val = re.split("[:=]", query)
            key = key.lower()
            # validation of query terms
            if key not in valid_terms:
                msg = "[ERROR] Valid query terms are: {0}"
                raise ValueError(msg.format(" ".join(valid_terms)))
            elif key in ["start", "end"]:
                try:
                    val = iso8601.parse_date(val).isoformat()
                except:
                    raise ValueError("start and end should be in ISO8601",
                                     "datetime format with mandatory offset",
                                     "and start cannot be after end")
            elif key == "status":
                if val not in valid_statuses:
                    msg = "[ERROR] Valid statuses are: {0}"
                    raise ValueError(msg.format(" ".join(valid_statuses)))
            terms.append("{0}={1}".format(key, val))

        query_string = "&".join(terms)
        endpoint = "http://{0}:{1}/{2}/query?{3}".format(
            self.host, self.secondary_port, self.endpoint, query_string
        )
        response = requests.get(endpoint, headers=self.headers)
        return response

    def get_status(self, workflowId):
        return self._get(workflowId, "status")

    def get_metadata(self, workflowId):
        return self._get(workflowId, "metadata")

    def get_logs(self, workflowId):
        return self._get(workflowId, "logs")

    def get_outputs(self, workflowId):
        return self._get(workflowId, "outputs")

    def abort(self, workflowId):
        endpoint = "http://{0}:{1}/{2}/{3}/abort".format(
            self.host, self.secondary_port, self.endpoint, workflowId
        )
        response = requests.post(endpoint, headers=self.headers)
        return response

    def _get(self, workflowId, action):
        valid_actions = ["status", "metadata", "logs", "outputs"]
        assert action in valid_actions
        endpoint = "http://{0}:{1}/{2}/{3}/{4}".format(
            self.host, self.secondary_port, self.endpoint, workflowId, action
        )
        response = requests.get(endpoint, headers=self.headers)
        return response
