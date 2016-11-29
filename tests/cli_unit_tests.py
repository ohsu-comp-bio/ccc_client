import argparse
import unittest

from nose.tools import eq_
from mock import patch, call

from ccc_client import cli


def calls_eq(mock_target_name, cliInput, expected_calls):
    '''
    Given a fully-qualified name of a method to mock and a string of
    CLI arguments to test, verify that the method was called as expected.

    e.g. calls_eq('ccc_client.Runner.method_name', 'svc action --arg', [
      call('expected_method_arg_1')
    ])
    '''
    with patch(mock_target_name) as mock:
        cli.cli_main(cliInput.split())
        eq_(mock.call_args_list, expected_calls)


class TestCommonArgs(unittest.TestCase):

    def testParseCommonArguments(self):
        cliInput = """dts get --port 8000 --host 127.0.0.1 --authToken foo bar"""
        args = cli.parser.parse_args(cliInput.split())
        self.assertEqual(args.port, "8000")
        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.authToken, "foo")
        self.assertEqual(args.debug, False)

def test_dts_post():
    cliInput ="""dts post --filepath /dev/null /dev/tty --user test
    --site central"""
    calls_eq('ccc_client.dts.DtsRunner.DtsRunner.post', cliInput, [
        call("/dev/null", ["central"], "test", None),
        call("/dev/tty", ["central"], "test", None)
    ])

def test_dts_put():
    cliInput = """dts put --filepath /dev/null --user test --site central
    --cccId foo
    """
    calls_eq('ccc_client.dts.DtsRunner.DtsRunner.put', cliInput, [
        call("foo", "/dev/null", ["central"], "test")
    ])

def test_dts_get():
    cliInput = """dts get foo"""
    calls_eq('ccc_client.dts.DtsRunner.DtsRunner.get', cliInput, [
        call('foo')
    ])

def test_dts_delete():
    cliInput = """dts delete foo"""
    calls_eq('ccc_client.dts.DtsRunner.DtsRunner.delete', cliInput, [
        call('foo')
    ])


def test_exec_submit():
    cliInput = """exec-engine submit --wdlSource /dev/null
    --workflowInputs /dev/null --workflowOptions /dev/tty
    """
    calls_eq(
        'ccc_client.exec_engine.ExecEngineRunner.ExecEngineRunner.submit_workflow',
        cliInput,
        [call('/dev/null', ['/dev/null'], '/dev/tty')]
    )

def test_exec_status():
    cliInput = """exec-engine status foo"""
    calls_eq(
        'ccc_client.exec_engine.ExecEngineRunner.ExecEngineRunner.get_status',
        cliInput,
        [call("foo")]
    )

def test_exec_outputs():
    cliInput = """exec-engine outputs foo"""
    calls_eq(
        'ccc_client.exec_engine.ExecEngineRunner.ExecEngineRunner.get_outputs',
        cliInput,
        [call("foo")]
    )

def test_exec_metadata():
    cliInput = """exec-engine metadata foo"""
    calls_eq(
        'ccc_client.exec_engine.ExecEngineRunner.ExecEngineRunner.get_metadata',
        cliInput,
        [call("foo")]
    )


def test_app_upload_image():
    cliInput = """app-repo upload-image --imageBlob /dev/null
    --imageName testImage --imageTag latest --metadata /dev/null
    """
    upload_image_fqn = 'ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_image'
    upload_metadata_fqn = 'ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_metadata'
    with patch(upload_image_fqn) as image_mock, \
         patch(upload_metadata_fqn) as meta_mock:

        cli.cli_main(cliInput.split())
        eq_(image_mock.call_args_list, [call("/dev/null", "testImage", "latest")])
        eq_(meta_mock.call_args_list, [call(None, "/dev/null")])

def test_app_upload_metadata():
    cliInput = """app-repo upload-metadata --metadata /dev/null --imageId foo """
    calls_eq(
        'ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_metadata',
        cliInput,
        [call("foo", "/dev/null")]
    )

def test_app_get_metadata():
    cliInput = """app-repo get-metadata foo"""
    calls_eq(
        'ccc_client.app_repo.AppRepoRunner.AppRepoRunner.get_metadata',
        cliInput,
        [call("foo")]
    )

def test_app_delete():
    cliInput = """app-repo delete-metadata foo"""
    calls_eq(
        'ccc_client.app_repo.AppRepoRunner.AppRepoRunner.delete_metadata',
        cliInput,
        [call("foo")]
    )


class testOptionParsing(unittest.TestCase):

    help_str = """usage: ccc_client mock test

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token
  --mock MOCK           mock argument"""

    stripped_common_args = """usage: ccc_client mock test

optional arguments:
  --mock MOCK           mock argument"""

    def testFindOptions(self):
        resp = cli.find_options(self.help_str, show_usage=True, strip_n=6)
        print(resp)
        self.assertEqual(resp, self.stripped_common_args)


class testHelpLong(unittest.TestCase):

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--debug",
                               default=False,
                               action="store_true",
                               help="debug flag")
    common_parser.add_argument("--host",
                               type=str,
                               help="host")
    common_parser.add_argument("--port",
                               type=str,
                               help="port")
    common_parser.add_argument("--authToken", "-T",
                               type=str,
                               help="authorization token")
    parser = argparse.ArgumentParser(description="Mock Parser",
                                     parents=[common_parser])
    parser.add_argument("--help-long",
                        default=False,
                        action="store_true",
                        help="Show help message for all services and actions")
    parser.add_argument("--version", action='version',
                        version="Test")
    subparsers = parser.add_subparsers(title="service", dest="service")
    mock = subparsers.add_parser("mock")
    mock_sub = mock.add_subparsers(title="action", dest="action")
    mock_test = mock_sub.add_parser("test", parents=[common_parser])
    mock_test.add_argument(
        "--mock",
        action="store_true",
        help="fake flag"
    )

    help_long = """usage: nosetests [-h] [--debug] [--host HOST] [--port PORT]
                 [--authToken AUTHTOKEN] [--help-long] [--version]
                 {mock} ...

Mock Parser

optional arguments:
  -h, --help            show this help message and exit
  --debug               debug flag
  --host HOST           host
  --port PORT           port
  --authToken AUTHTOKEN, -T AUTHTOKEN
                        authorization token
  --help-long           Show help message for all services and actions
  --version             show program's version number and exit

service:
  {mock}

============================================================
mock
============================================================
usage: nosetests mock [-h] {test} ...

action:
  {test}

--------
| test |
--------
usage: nosetests mock test [-h] [--debug] [--host HOST] [--port PORT]
                           [--authToken AUTHTOKEN] [--mock]

optional arguments:
  --mock                fake flag
"""

    def testHelpLong(self):
        resp = cli.display_help(self.parser)
        self.assertEqual(resp, self.help_long)
