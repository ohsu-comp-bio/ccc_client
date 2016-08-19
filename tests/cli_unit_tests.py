import unittest

from ccc_client import cli, DtsRunner, ExecEngineRunner, AppRepoRunner, ElasticSearchRunner


class TestCommonArgs(unittest.TestCase):

    def testParseArguments(self):
        cliInput = """--port 8000 --host 127.0.0.1 --authToken foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.port, "8000")
        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.authToken, "foo")
        self.assertEqual(args.debug, False)


class TestDtsArgs(unittest.TestCase):

    def testParseArgumentsPost(self):
        cliInput = """dts post --filepath /dev/null /dev/null --user test
        --site central
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.filepath, ["/dev/null", "/dev/null"])
        self.assertEqual(args.user, "test")
        self.assertEqual(args.site, ["central"])
        self.assertEqual(args.runner, DtsRunner)
        self.assertEqual(args.action, "post")

    def testParseArgumentsPut(self):
        cliInput = """dts put --filepath /dev/null --user test --site central
        --cccId foo
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.filepath, "/dev/null")
        self.assertEqual(args.user, "test")
        self.assertEqual(args.site, ["central"])
        self.assertEqual(args.cccId, "foo")
        self.assertEqual(args.runner, DtsRunner)
        self.assertEqual(args.action, "put")

    def testParseArgumentsGet(self):
        cliInput = """dts get foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.cccId, ["foo"])
        self.assertEqual(args.runner, DtsRunner)
        self.assertEqual(args.action, "get")

    def testParseArgumentsDelete(self):
        cliInput = """dts delete foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.cccId, ["foo"])
        self.assertEqual(args.runner, DtsRunner)
        self.assertEqual(args.action, "delete")


class TestExecEngineArgs(unittest.TestCase):

    def testParseArgumentsSubmit(self):
        cliInput = """exec-engine submit --wdlSource /dev/null
        --workflowInputs /dev/null --workflowOptions /dev/null
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.wdlSource, "/dev/null")
        self.assertEqual(args.workflowInputs, ["/dev/null"])
        self.assertEqual(args.workflowOptions, "/dev/null")
        self.assertEqual(args.runner, ExecEngineRunner)
        self.assertEqual(args.action, "submit")

    def testParseArgumentsStatus(self):
        cliInput = """exec-engine status foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.workflowId, "foo")
        self.assertEqual(args.runner, ExecEngineRunner)
        self.assertEqual(args.action, "status")

    def testParseArgumentsOutputs(self):
        cliInput = """exec-engine outputs foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.workflowId, "foo")
        self.assertEqual(args.runner, ExecEngineRunner)
        self.assertEqual(args.action, "outputs")

    def testParseArgumentsMetadata(self):
        cliInput = """exec-engine metadata foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.workflowId, "foo")
        self.assertEqual(args.runner, ExecEngineRunner)
        self.assertEqual(args.action, "metadata")


class TestAppRepoArgs(unittest.TestCase):

    def testParseArgumentsPost(self):
        cliInput = """app-repo post --imageBlob /dev/null
        --imageName testImage --imageTag latest --metadata /dev/null
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.imageBlob, "/dev/null")
        self.assertEqual(args.imageName, "testImage")
        self.assertEqual(args.imageTag, "latest")
        self.assertEqual(args.metadata, "/dev/null")
        self.assertEqual(args.runner, AppRepoRunner)
        self.assertEqual(args.action, "post")

    def testParseArgumentsPut(self):
        cliInput = """app-repo put --metadata /dev/null --imageId foo """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.imageId, "foo")
        self.assertEqual(args.metadata, "/dev/null")
        self.assertEqual(args.runner, AppRepoRunner)
        self.assertEqual(args.action, "put")

    def testParseArgumentsGet(self):
        cliInput = """app-repo get foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.imageId, "foo")
        self.assertEqual(args.runner, AppRepoRunner)
        self.assertEqual(args.action, "get")

    def testParseArgumentsDelete(self):
        cliInput = """app-repo delete foo"""
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.imageId, "foo")
        self.assertEqual(args.runner, AppRepoRunner)
        self.assertEqual(args.action, "delete")


class TestElasticSearchArgs(unittest.TestCase):

    def testParseArgumentsQuery(self):
        cliInput = """elasticsearch query --domain patient --query-terms foo:bar
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.domain, "patient")
        self.assertEqual(args.query_terms, ["foo:bar"])
        self.assertEqual(args.runner, ElasticSearchRunner)
        self.assertEqual(args.action, "query")

    def testParseArgumentsPublishBatch(self):
        cliInput = """elasticsearch publish-batch --tsv /dev/null --site ohsu
        --user test --project foo --domain patient --domainJson /dev/null
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.tsv, "/dev/null")
        self.assertEqual(args.site, "ohsu")
        self.assertEqual(args.user, "test")
        self.assertEqual(args.project, "foo")
        self.assertEqual(args.domain, "patient")
        self.assertEqual(args.domainJson, "/dev/null")
        self.assertEqual(args.isMock, False)
        self.assertEqual(args.skipDtsRegistration, False)
        self.assertEqual(args.runner, ElasticSearchRunner)
        self.assertEqual(args.action, "publish-batch")

    def testParseArgumentsPublishResource(self):
        cliInput = """elasticsearch publish-resource --filepath /dev/null
        --mimeType text --inheritFrom blah --propertyOverride 1:2 --site ohsu
        --user test --project foo --workflowId bar --domainJson /dev/null
        --mock --skipDtsRegistration
        """
        parser = cli.setup_parser()
        args = parser.parse_args(cliInput.split())
        self.assertEqual(args.filepath, "/dev/null")
        self.assertEqual(args.mimeType, "text")
        self.assertEqual(args.inheritFrom, "blah")
        self.assertEqual(args.propertyOverride, ["1:2"])
        self.assertEqual(args.site, "ohsu")
        self.assertEqual(args.user, "test")
        self.assertEqual(args.project, "foo")
        self.assertEqual(args.workflowId, "bar")
        self.assertEqual(args.domainJson, "/dev/null")
        self.assertEqual(args.isMock, True)
        self.assertEqual(args.skipDtsRegistration, True)
        self.assertEqual(args.runner, ElasticSearchRunner)
        self.assertEqual(args.action, "publish-resource")

