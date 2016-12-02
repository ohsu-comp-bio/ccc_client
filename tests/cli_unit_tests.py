import argparse
import unittest

from nose.tools import eq_
from mock import patch, call

from ccc_client import cli


def run_cli(args):
    '''Run the CLI for tests, with extra help.'''
    return cli.cli_main(['ccc_client'] + args.split())


def calls_eq(mock_target_name, cliInput, expected_calls):
    '''
    Given a fully-qualified name of a method to mock and a string of
    CLI arguments to test, verify that the method was called as expected.
    e.g. calls_eq('ccc_client.Runner.method_name', 'svc action --arg', [
      call('expected_method_arg_1')
    ])
    '''
    with patch(mock_target_name) as mock:
        run_cli(cliInput)
        eq_(mock.call_args_list, expected_calls)


def test_common_args():
    cliInput = "dts get --port 8000 --host 127.0.0.1 --authToken foo bar"
    args = cli.parser.parse_args(cliInput.split())
    eq_(args.port, "8000")
    eq_(args.host, "127.0.0.1")
    eq_(args.authToken, "foo")
    eq_(args.debug, False)


@patch('ccc_client.dts.DtsRunner.DtsRunner.post')
def test_dts_post(mock):
    run_cli("dts post --filepath /dev/null /dev/tty "
            "--user test --site central")
    eq_(mock.call_args_list, [
        call("/dev/null", ["central"], "test", None),
        call("/dev/tty", ["central"], "test", None)
    ])


@patch('ccc_client.dts.DtsRunner.DtsRunner.put')
def test_dts_put(mock):
    run_cli("dts put --filepath /dev/null --user test --site central "
            "--cccId foo")
    eq_(mock.call_args_list, [
        call("foo", "/dev/null", ["central"], "test")
    ])


@patch('ccc_client.dts.DtsRunner.DtsRunner.get')
def test_dts_get(mock):
    run_cli("dts get foo")
    eq_(mock.call_args_list, [call('foo')])


@patch('ccc_client.dts.DtsRunner.DtsRunner.delete')
def test_dts_delete(mock):
    run_cli("dts delete foo")
    eq_(mock.call_args_list, [call('foo')])


@patch('ccc_client.exec_engine.ExecEngineRunner'
       '.ExecEngineRunner.submit_workflow')
def test_exec_submit(mock):
    run_cli("exec-engine submit --wdlSource /dev/null "
            "--workflowInputs /dev/null --workflowOptions /dev/tty")
    eq_(mock.call_args_list, [
        call('/dev/null', ['/dev/null'], '/dev/tty')
    ])


@patch('ccc_client.exec_engine.ExecEngineRunner'
       '.ExecEngineRunner.get_status')
def test_exec_status(mock):
    run_cli("exec-engine status foo")
    eq_(mock.call_args_list, [call("foo")])


@patch('ccc_client.exec_engine.ExecEngineRunner'
       '.ExecEngineRunner.get_outputs')
def test_exec_outputs(mock):
    run_cli("exec-engine outputs foo")
    eq_(mock.call_args_list, [call("foo")])


@patch('ccc_client.exec_engine.ExecEngineRunner'
       '.ExecEngineRunner.get_metadata')
def test_exec_metadata(mock):
    run_cli("exec-engine metadata foo")
    eq_(mock.call_args_list, [call("foo")])


@patch('ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_metadata')
@patch('ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_image')
def test_app_upload_image(image_mock, meta_mock):
    run_cli("app-repo upload-image --imageBlob /dev/null "
            "--imageName testImage --imageTag latest --metadata /dev/null")
    eq_(image_mock.call_args_list, [
        call("/dev/null", "testImage", "latest")
    ])
    eq_(meta_mock.call_args_list, [call(None, "/dev/null")])


@patch('ccc_client.app_repo.AppRepoRunner.AppRepoRunner.upload_metadata')
def test_app_upload_metadata(mock):
    run_cli("app-repo upload-metadata --metadata /dev/null --imageId foo")
    eq_(mock.call_args_list, [call("foo", "/dev/null")])


@patch('ccc_client.app_repo.AppRepoRunner.AppRepoRunner.get_metadata')
def test_app_get_metadata(mock):
    run_cli("app-repo get-metadata foo")
    eq_(mock.call_args_list, [call("foo")])


@patch('ccc_client.app_repo.AppRepoRunner.AppRepoRunner.delete_metadata')
def test_app_delete(mock):
    run_cli("app-repo delete-metadata foo")
    eq_(mock.call_args_list, [call("foo")])


@patch('ccc_client.eve_mongo.EveMongoRunner.EveMongoRunner.status')
def test_app_em_status(mock):
    run_cli("eve-mongo status")


@patch('ccc_client.eve_mongo.EveMongoRunner.EveMongoRunner.query')
def test_app_em_query(mock):
    run_cli('eve-mongo query -e files -f foo')
    eq_(mock.call_args_list, [call("files", "foo")])


@patch('ccc_client.eve_mongo.EveMongoRunner.EveMongoRunner.publish')
def test_app_em_publish(mock):
    run_cli("eve-mongo publish --tsv /dev/null --site ohsu "
            "--user testUser --program testProgram --project testProject "
            "--domain file --domainJson /dev/null")
    eq_(mock.call_args_list, [
        call("/dev/null", "ohsu", "testUser", "testProgram",
             "testProject", "file", "/dev/null")
    ])


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
    parser = argparse.ArgumentParser(prog="ccc_client",
                                     description="Mock Parser",
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

    help_long = """usage: ccc_client [-h] [--debug] [--host HOST] [--port PORT]
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
usage: ccc_client mock [-h] {test} ...

action:
  {test}

--------
| test |
--------
usage: ccc_client mock test [-h] [--debug] [--host HOST] [--port PORT]
                            [--authToken AUTHTOKEN] [--mock]

optional arguments:
  --mock                fake flag
"""

    def testHelpLong(self):
        resp = cli.display_help(self.parser)
        self.maxDiff = None
        self.assertMultiLineEqual(resp, self.help_long)
