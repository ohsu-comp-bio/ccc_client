"""
Command line utility for interacting with CCC services.
"""
from __future__ import print_function

import argparse
import glob
import itertools
import json
import os
import re
import requests
import sys
import uuid


def display_help(parser):
    """
    This function is called from customParser to "hijack" the help message
    :return:
    """
    # Print main help message
    print(parser.format_help())

    # Find all service subparsers
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]

    # Iterate through the services
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():

            # Find all actions for service
            method_subparser_actions = [
                action for action in subparser._actions
                if isinstance(action, argparse._SubParsersAction)
            ]

            # Print service help
            print("=" * 60)
            print("{0}".format(choice))
            print("=" * 60)
            print(find_options(subparser.format_help()))

            # Iterate through the actions for a service
            for method_subparser_action in method_subparser_actions:
                for method_choice, method_subparser in method_subparser_action.choices.items():
                    # Print service action help
                    print("-" * len("| {0} |".format(method_choice)))
                    print("| {0} |".format(method_choice))
                    print("-" * len("| {0} |".format(method_choice)))
                    print(find_options(method_subparser.format_help()))


def find_options(helptext, show_help=False, show_usage=True):
    """
    Return a substring with the optional arguments
    :param helptext: Help text, as it"s called
    :return:
    """
    helplist = helptext.split("\n")

    # Remove usage info
    if not show_usage:
        helplist = helplist[helplist.index("optional arguments:"):]

    # Remove help flag info
    if not show_help:
        del helplist[helplist.index("optional arguments:") + 1]

    # Handle cases where there are no optional arguments
    if helplist[helplist.index("optional arguments:") + 1] == "":
        del helplist[helplist.index("optional arguments:") + 1]
        del helplist[helplist.index("optional arguments:")]

    return "\n".join(helplist)


def setup_parser():
    parser = argparse.ArgumentParser(description="CCC client")
    parser.add_argument("--debug",
                        default=False,
                        action="store_true",
                        help="debug flag")
    parser.add_argument("--extra-help",
                        default=False,
                        action="store_true",
                        help="Show help message for all services and actions")

    subparsers = parser.add_subparsers(title="service", dest="service")

    ##
    # DTS
    ##
    dts = subparsers.add_parser("dts")
    dts.add_argument("--host",
                     type=str,
                     default="central-gateway.ccc.org",
                     choices=["0.0.0.0",
                              "central-gateway.ccc.org",
                              "docker-centos7"],
                     help="host")
    dts.add_argument("--port",
                     type=str,
                     default="9510",
                     help="port")
    dts.set_defaults(runner=DtsRunner)

    dts_sub = dts.add_subparsers(title="action", dest="action")

    # api/v1/dts/file
    dts_post = dts_sub.add_parser("post")
    dts_post.add_argument(
        "--filepath", "-f",
        required=True,
        type=str,
        nargs="+",
        help="name of file(s) or pattern to glob on"
    )
    dts_post.add_argument(
        "--user", "-u",
        required=True,
        type=str,
        help="site user")
    dts_post.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )

    # api/v1/dts/file/<uuid>
    dts_get = dts_sub.add_parser("get")
    dts_get.add_argument(
        "--cccId",
        required=True,
        type=str,
        nargs="+",
        help="cccId entry to GET"
    )

    # api/v1/dts/file/<uuid>
    dts_delete = dts_sub.add_parser("delete")
    dts_delete.add_argument(
        "--cccId",
        required=True,
        type=str,
        nargs="+",
        help="cccId entry to DELETE"
    )

    ##
    # App Repo
    ##
    ar = subparsers.add_parser("app-repo")
    ar.add_argument("--host",
                    type=str,
                    default="docker-centos7",
                    choices=["0.0.0.0",
                             "central-gateway.ccc.org",
                             "docker-centos7"],
                    help="host")
    ar.add_argument("--port",
                    type=str,
                    default="8082",
                    help="port")
    ar.set_defaults(runner=AppRepoRunner)

    ar_sub = ar.add_subparsers(title="action", dest="action")

    # api/v1/tool/
    ar_post = ar_sub.add_parser("post")
    ar_post.add_argument(
        "--filepath", "-f", type=str, help="name of file or path"
    )
    ar_post.add_argument(
        "--imageName", "-n", type=str, help="name of docker image"
    )
    ar_post.add_argument(
        "--imageTag", "-t", type=str, default="latest",
        help="docker image version tag"
    )
    ar_post.add_argument(
        "--metadata", "-m", type=str,
        help="tool metadata"
    )

    # api/v1/tool/<uuid>
    ar_put = ar_sub.add_parser("put")
    ar_put.add_argument(
        "--metadata", "-m", type=str,
        help="tool metadata"
    )
    ar_put.add_argument(
        "--imageId", "-i", type=str,
        help="docker image id"
    )

    # api/v1/tool/<uuid>
    # api/v1/tool/<tool_name>/data
    ar_get = ar_sub.add_parser("get")
    ar_get.add_argument(
        "--imageId", "-i", type=str,
        help="docker image id"
    )

    # api/v1/tool/<uuid>
    ar_delete = ar_sub.add_parser("delete")
    ar_delete.add_argument(
        "--imageId", "-i", type=str,
        help="docker image id"
    )

    ##
    # Exec Engine
    ##
    ee = subparsers.add_parser("exec-engine")
    ee.add_argument("--host",
                    type=str,
                    default="0.0.0.0",
                    choices=["0.0.0.0",
                             "central-gateway.ccc.org",
                             "docker-centos7"],
                    help="host")
    ee.add_argument("--port",
                    type=str,
                    default="8000",
                    help="port")    
    ee.set_defaults(runner=ExecEngineRunner)

    ee_sub = ee.add_subparsers(title="action", dest="action")

    # api/workflows/v1/
    ee_post = ee_sub.add_parser("submit")
    ee_post.add_argument(
        "--wdlSource", "-s",
        type=str,
        help="name of file or path"
    )
    ee_post.add_argument(
        "--workflowInputs", "-i",
        type=str,
        help="name of docker image"
    )
    ee_post.add_argument(
        "--workflowOptions", "-o",
        type=str,
        default="-",
        help="docker image version tag"
    )

    # api/workflows/v1/<uuid>/status
    ee_status = ee_sub.add_parser("status")
    ee_status.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/outputs
    ee_outputs = ee_sub.add_parser("outputs")
    ee_outputs.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/metadata
    ee_meta = ee_sub.add_parser("metadata")
    ee_meta.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    return parser


class DtsRunner(object):
    """
    Send requests to the DTS
    """
    def __init__(self, args):
        self.args = args
        self.port = args.port
        self.endpoint = "api/v1/dts/file"
        self.action = args.action

        if self.action == "post":
            self.site = args.site
            self.filepath = list(itertools.chain.from_iterable(
                [glob.glob(f) for f in args.filepath]
            ))
            self.user = args.user
        else:
            self.cccId = args.cccId

    def run(self):
        if self.action == "post":
            self.__post_entry()
        elif self.action == "get":
            self.__get_entry()
        elif self.action == "delete":
            self.__delete_entry()
        else:
            raise RuntimeError("Unsupported action: {0}".format(self.action))

    def __get_entry(self):
        response = []
        for cccId in self.cccId:
            endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                       self.endpoint, cccId)
            headers = {'Content-Type': 'application/json'}
            r = requests.get(endpoint, headers=headers)
            response.append(r.content)
        return response

    def __delete_entry(self):
        response = []
        for cccId in self.cccId:
            endpoint = "http://{0}:{1}/{2}/{3}".format(self.host, self.port,
                                                       self.endpoint, cccId)
            headers = {'Content-Type': 'application/json'}
            r = requests.delete(endpoint, headers=headers)
            response.append(r.content)
        return response

    def __post_entry(self):
        # remap site name to IP
        site_map = {"central": "10.73.127.1",
                    "ohsu": "10.73.127.6",
                    "dfci": "10.73.127.18",
                    "oicr": "10.73.127.14"}

        response = []
        for filepath in self.filepath:
            if not os.path.isfile(filepath):
                raise RuntimeError(
                    "{0} was not found on the file system".format(filepath)
                )

            data = {}

            data['cccId'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, filepath))
            data['name'] = os.path.basename(filepath)
            data['size'] = os.path.getsize(filepath)
            location = {}
            location['site'] = site_map[self.site]
            location['path'] = os.path.dirname(os.path.abspath(filepath))
            location['timestampUpdated'] = os.stat(filepath)[-2]
            location['user'] = {"name": self.user}
            data['location'] = [location]

            endpoint = "http://{0}:{1}/{2}".format(self.host, self.port,
                                                   self.endpoint)
            headers = {'Content-Type': 'application/json'}
            r = requests.post(endpoint, data=json.dumps(data), headers=headers)

            print("{0}    {1}".format(os.path.abspath(filepath),
                                      data['cccId']))
            response.append(r.content)
        return response


class AppRepoRunner(object):
    """
    Send requests to the AppRepo
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.action = args.action

        if self.action == "post":
            self.blob = args.filepath
            self.imageTag = args.imageTag

            if args.name is None:
                self.imageName = re.sub("(\.tar)", "",
                                        os.path.dirname(args.filepath))
            else:
                self.imageName = args.imageName

            try:
                with open(args.metadata) as metadata:
                    self.metadata = json.loads(metadata)
            except Exception:
                self.metadata = None

        if self.action == "put":
            with open(args.metadata) as metadata:
                self.metadata = json.loads(metadata)

            if args.imageId is not None:
                self.imageId = args.imageId
            else:
                self.imageId = str(uuid.uuid4())
                self.metadata['id'] = self.imageId

            assert self.imageId == self.metadata['id']

        if self.action in ["get", "delete"]:
            self.imageId = args.imageId

    def run(self):
        if self.action == "post":
            if self.blob is not None:
                self.__post_blob()

            if self.metadata is not None:
                self.__put_metadata()

    def __post_blob(self):
        endpoint = "http://{0}:{1}/api/v1/tool/".format(self.host, self.port)

        form_data = {'file': open(self.blob, 'rb'),
                     "imageName": (None, self.imageName),
                     "imageTag": (None, self.imageTag)}

        response = requests.post(endpoint, files=form_data)

        self.imageId = re.compile(
            r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}').findall(
                response.content)[0]

        return response.content

    def __put_metadata(self):
        endpoint = "http://{0}:{1}/api/v1/tool/{2}".format(self.host,
                                                           self.port,
                                                           self.toolId)
        response = requests.put(endpoint, data=json.dumps(self.metadata))
        return response.content


class ExecEngineRunner(object):
    """
    Send requests to the Execution Engine
    """
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.action = args.action

        if self.action == "submit":
            self.wdlSource = args.wdlSource
            self.workflowInputs = args.workflowInputs
        else:
            self.workflowId = args.workflowId

    def run(self):
        if self.action == "submit":
            self.__submit_workflow()
        elif self.action == "status":
            self.__get_status()
        elif self.action == "metadata":
            self.__get_metadata()
        elif self.action == "outputs":
            self.__get_outputs()
        else:
            raise RuntimeError("Unsupported action: {0}".format(self.action))

    def __submit_workflow(self):
        endpoint = "http://{0}:{1}/api/workflows/v1".format(self.host,
                                                            self.port)

        form_data = {'wdlSource': open(self.wdlSource, 'rb'),
                     'workflowInputs': open(self.workflowInputs, 'rb')}

        response = requests.post(endpoint, files=form_data)
        return response.content

    def __get_status(self):
        endpoint = "http://{0}:{1}/api/workflows/v1/{2}/status".format(
            self.host, self.port, self.workflowId
        )

        response = requests.get(endpoint)
        return response.content

    def __get_metadata(self):
        endpoint = "http://{0}:{1}/api/workflows/v1/{2}/metadata".format(
            self.host, self.port, self.workflowId
        )

        response = requests.get(endpoint)
        return response.content

    def __get_outputs(self):
        endpoint = "http://{0}:{1}/api/workflows/v1/{2}/outputs".format(
            self.host, self.port, self.workflowId
        )

        response = requests.get(endpoint)
        return response.content


def client_main():
    parser = setup_parser()

    if "--extra-help" in sys.argv[1:]:
        return display_help(parser)

    args = parser.parse_args()

    if "runner" not in args:
        parser.print_help()
    else:
        try:
            runner = args.runner(args)
            response = runner.run()
            if response is not None:
                print(response)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    client_main()
