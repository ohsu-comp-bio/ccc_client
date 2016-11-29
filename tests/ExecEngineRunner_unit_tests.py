import unittest
import tempfile
import json

from mock import patch
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

    invalid_wdl_filepath = "/ZAfvcacADF/fakeWdl.wdl"

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
        # mimic successful post with single input json
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.text = mock_response
            resp = self.ee_client.submit_workflow(
                wdlSource=self.mock_wdl_filepath,
                workflowInputs=self.mock_json_filepath,
                workflowOptions=None,
            )
            self.assertEqual(resp.text, mock_response)

        # mimic successful post with multiple input jsons
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
            with self.assertRaises(IOError):
                self.ee_client.submit_workflow(
                    wdlSource=self.invalid_wdl_filepath,
                    workflowInputs=self.mock_json_filepath,
                    workflowOptions=None,
                )

        # pass inputs file incorrectly
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            with self.assertRaises(TypeError):
                self.ee_client.submit_workflow(
                    wdlSource=self.mock_wdl_filepath,
                    workflowInputs={'workflowInputs': self.mock_json_filepath},
                    workflowOptions=None,
                )

    def test_ee_query(self):
        # mimic successful get request to query endpoint
        terms = ["Status:Submitted", "name=testWorkflow"]
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.ee_client.query(
                terms
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:8000/api/workflows/v1/query?status=Submitted&name=testWorkflow",
                headers={'Authorization': 'Bearer '}
            )

        # invalid search term
        terms = ["task:foobar"]
        with patch('requests.get') as mock_get:
            with self.assertRaises(ValueError):
                self.ee_client.query(
                    terms
                )

        # invalid status
        terms = ["Status:foobar", "name=testWorkflow"]
        with patch('requests.get') as mock_get:
            with self.assertRaises(ValueError):
                self.ee_client.query(
                    terms
                )

    def test_ee_status(self):
        # mimic successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.ee_client.get_status(
                workflowId=self.mock_workflow_id
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:8000/api/workflows/v1/{0}/status".format(self.mock_workflow_id),
                headers={'Authorization': 'Bearer '}
            )

    def test_ee_metadata(self):
        # mimic successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.ee_client.get_metadata(
                workflowId=self.mock_workflow_id
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:8000/api/workflows/v1/{0}/metadata".format(self.mock_workflow_id),
                headers={'Authorization': 'Bearer '}
            )

    def test_ee_outputs(self):
        # mimic successful get request to status endpoint
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 201
            self.ee_client.get_outputs(
                workflowId=self.mock_workflow_id
            )
            mock_get.assert_called_with(
                "http://central-gateway.ccc.org:8000/api/workflows/v1/{0}/outputs".format(self.mock_workflow_id),
                headers={'Authorization': 'Bearer '}
            )


if __name__ == '__main__':
    unittest.main()
