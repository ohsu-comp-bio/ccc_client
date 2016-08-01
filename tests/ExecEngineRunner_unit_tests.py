import unittest
import tempfile
import json

from unittest.mock import patch
from ccc_client import ExecEngineRunner


class TestExecEngineRunner(unittest.TestCase):
    ee_client = ExecEngineRunner()

    mock_wdl = tempfile.NamedTemporaryFile(delete=False)
    mock_wdl_filepath = mock_wdl.name
    mock_wdl_content = """
task hello {
  String name

  command {
    echo 'Hello ${name}!'
  }

  output {
    File response = stdout()
  }
}

workflow test {
  call hello
}
"""

    mock_json = tempfile.NamedTemporaryFile(delete=False)
    mock_json_filepath = mock_json.name
    mock_json_content = json.dumps(
        {
            "test.hello.name": "World"
        }
    )

    mock_workflow_id = "6dd5114a-3a6b-4ee8-9d50-bdec075998b4"

    def test_ee_submit(self):
        mock_response = json.dumps(
            {
                "multipleInputs": {
                    self.mock_workflow_id: self.mock_json_filepath,
                }
            }
        )
        # mimick successful post with single input json
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = mock_response
            resp = self.ee_client.submit_workflow(
                wdlSource=self.mock_wdl_filepath,
                workflowInputs=self.mock_json_filepath,
                workflowOptions=None,
            )
            self.assertEqual(resp.text, mock_response)

        # mimick successful post with multiple input jsons
        mock_response = json.dumps(
            {
                "multipleInputs": {
                    self.mock_workflow_id: self.mock_json_filepath,
                    self.mock_workflow_id: self.mock_json_filepath,
                }
            }
        )
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = mock_response
            resp = self.ee_client.submit_workflow(
                wdlSource=self.mock_wdl_filepath,
                workflowInputs=[self.mock_json_filepath, self.mock_json_filepath],
                workflowOptions=None,
            )
            self.assertEqual(resp.text, mock_response)

        # pass path to wdl that does not exist
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with self.assertRaises(FileNotFoundError):
                resp = self.ee_client.submit_workflow(
                    wdlSource="/tmp/fakeWdl.wdl",
                    workflowInputs=self.mock_json_filepath,
                    workflowOptions=None,
                )

        # pass inputs file incorrectly
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with self.assertRaises(TypeError):
                resp = self.ee_client.submit_workflow(
                    wdlSource=self.mock_wdl_filepath,
                    workflowInputs={'workflowInputs': self.mock_json_filepath},
                    workflowOptions=None,
                )

    def test_ee_status(self):
        mock_response = json.dumps(
            {
                "id": self.mock_workflow_id,
                "status": "Running"
            }
        )
        # mimick successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = mock_response
            resp = self.ee_client.get_status(
                    workflowId=self.mock_workflow_id
            )
            self.assertEqual(resp.text, mock_response)

    def test_ee_metadata(self):
        mock_response = json.dumps(
            {
                "workflowName": "hello",
                "calls": {
                    "test.hello": [
                        {
                            "executionStatus": "Done",
                            "stdout": "/home/cromwell-executions/test/" + self.mock_workflow_id + "/call-hello/stdout",
                            "shardIndex": -1,
                            "outputs": {
                                "response": "World"
                            },
                            "inputs": {
                                "name": "World"
                            },
                            "runtimeAttributes": {},
                            "returnCode": 0,
                            "backend": "Local",
                            "end": "2016-02-04T13:47:56.000-05:00",
                            "stderr": "/home/cromwell-executions/test/" + self.mock_workflow_id + "/call-hello/stderr",
                            "attempt": 1,
                            "executionEvents": [],
                            "start": "2016-02-04T13:47:55.000-05:00"
                        }
                    ]
                },
                "id": self.mock_workflow_id,
                "outputs": {
                    "test.hello.response": "World"
                },
                "inputs": {
                    "test.hello.name": "World"
                },
                "submission": "2016-02-04T13:47:55.000-05:00",
                "status": "Succeeded",
                "end": "2016-02-04T13:47:57.000-05:00",
                "start": "2016-02-04T13:47:55.000-05:00"
            }
        )
        # mimick successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = mock_response
            resp = self.ee_client.get_metadata(
                    workflowId=self.mock_workflow_id
            )
            self.assertEqual(resp.text, mock_response)

    def test_ee_outputs(self):
        mock_response = json.dumps(
            {
                "id": self.mock_workflow_id,
                "outputs": {
                    "test.hello.response": "World"
                }
            }
        )
        # mimick successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            mock_get.return_value.text = mock_response
            resp = self.ee_client.get_outputs(
                    workflowId=self.mock_workflow_id
            )
            self.assertEqual(resp.text, mock_response)


if __name__ == '__main__':
    unittest.main()
