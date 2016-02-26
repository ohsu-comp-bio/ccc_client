"""
Command line utility for interacting with CCC services.
"""
from __future__ import print_function

import argparse
import json
import os
import re
import requests

from uuid import NAMESPACE_OID as noid, uuid5


# ------------------------------
# Misc
# ------------------------------
def add_subparser(subparsers, subcommand, description):
    parser = subparsers.add_parser(
        subcommand, description=description, help=description
    )
    return parser


# ------------------------------
# DTS
# ------------------------------
def add_dts_parser(subparsers):
    parser = add_subparser(subparsers, "dts", "Interact with the DTS")
    parser.add_argument(
        '--host', '-d', type=str, default="http://0.0.0.0", help='host'
    )
    parser.add_argument(
        '--port', '-p', type=str, default="9510", help='port'
    )
    parser.add_argument(
        '--filepath', '-f', required=True, type=str,
        help='name of file or path'
    )
    parser.add_argument(
        '--user', '-u', required=True, type=str, help='site user')
    parser.add_argument(
        '--site', '-s', required=True, type=str,
        choices=["g1.spark0.intel.com", "central-gateway.ccc.org",
                 "pdx-gateway.ccc.org", "dfci-gateway.ccc.org", 
                 "boston-gateway.ccc.org"],
        help='site the data resides at'
    )
    parser.set_defaults(runner=DtsRunner)
    return parser


class DtsRunner(object):
    """
    Send requests to the DTS
    """
    def __init__(self, args):
        super(DtsRunner, self).__init__(args)
        self.host = re.sub('(http|https|://)', '', args.host)
        self.port = args.port
        self.site = args.site
        self.name = os.path.basename(args.filepath)
        self.path = os.path.dirname(args.filepath)
        self.size = os.path.getsize(args.filepath)
        self.user = args.user
        self.cccId = str(uuid5(noid, args.filepath))
        self.timestampUpdated = os.stat(args.filepath)[-2]

    def run(self):
        data = {}
        data['cccId'] = self.cccId
        data['name'] = self.name
        data['size'] = self.size
        location = {}
        location['site'] = self.site
        location['path'] = self.path
        location['timestampUpdated'] = self.timestampUpdated
        location['user'] = {"name": self.user}
        data['location'] = [location]

        headers = {'Content-Type': 'application/json'}
        endpoint = "http://{0}:{1}/api/v1/dts/file".format(self.host, self.port)

        response = requests.post(endpoint, data=json.dumps(data), headers=headers)
        return response.content


# ------------------------------
# AppRepo
# ------------------------------
def add_apprepo_parser(subparsers):
    parser = add_subparser(subparsers, "app-repo", "Interact with the App Repo")
    parser.add_argument(
        '--host', '-d', type=str, default="http://0.0.0.0", help='host'
    )
    parser.add_argument(
        '--port', '-p', type=str, default="8082", help='port'
    )
    parser.add_argument(
        '--filepath', '-f', type=str, help='name of file or path'
    )
    parser.add_argument(
        '--imageName', '-n', type=str, help='name of docker image'
    )
    parser.add_argument(
        '--imageTag', '-t', type=str, default="latest",
        help='docker image version tag'
    )
    parser.add_argument(
        '--metadata', '-m', type=str,
        help='tool metadata'
    )
    parser.add_argument(
        '--imageId', '-i', type=str,
        help='docker image id'
    )
    parser.set_defaults(runner=AppRepoRunner)
    return parser


class AppRepoRunner(object):
    """
    Send requests to the AppRepo
    """
    def __init__(self, args):
        super(DtsRunner, self).__init__(args)
        self.host = re.sub('(http|https|://)', '', args.host)
        self.port = args.port
        self.blob = args.filepath
        self.imageId = args.imageId
        self.imageTag = args.imageTag

        if args.name is None:
            self.imageName = re.sub("(\.tar)", "", os.path.dirname(args.filepath))
        else:
            self.imageName = args.imageName

        try:
            with open(args.metadata) as metadata:
                self.metadata = json.loads(metadata)
        except Exception:
            self.metadata = None

    def run(self):
        if self.blob is not None:
            self.post_blob()

        if (self.metadata is not None) and (self.imageId is not None):
            self.post_metadata()

    def post_blob(self):
        headers = {'Content-Type': 'multipart/form-data'}
        endpoint = "http://{0}:{1}/api/v1/tool/".format(self.host, self.port)

        response = requests.post(endpoint, data="", headers=headers)
        return response.content

    def post_metadata(self):
        headers = {'Content-Type': 'application/json'}
        endpoint = "http://{0}:{1}/api/v1/tool/{2}".format(self.host, self.port, self.toolId)

        response = requests.put(endpoint, data=self.metadata, headers=headers)
        return response.content


# ------------------------------
# Exec Engine
# ------------------------------
def add_execengine_parser(subparsers):
    parser = add_subparser(subparsers, "exec-engine", "Interact with the Execution Engine")
    parser.add_argument(
        '--host', '-d', type=str, default="http://0.0.0.0", help='host'
    )
    parser.add_argument(
        '--port', '-p', type=str, default="8000", help='port'
    )
    parser.add_argument(
        '--wdlSource', type=str, help='WDL workflow file'
    )
    parser.add_argument(
        '--inputJson', type=str, help='WDL inputs json file'
    )
    parser.set_defaults(runner=ExecEngineRunner)
    return parser


# ------------------------------
# client entrypoint
# ------------------------------
def get_ccc_client_parser():
    parser = argparse.ArgumentParser(
        description="CCC client")
    subparsers = parser.add_subparsers(title='subcommands',)
    add_dts_parser(subparsers)
    add_apprepo_parser(subparsers)
    add_execengine_parser(subparsers)
    return parser


def client_main(args=None):
    parser = get_ccc_client_parser()
    args = parser.parse_args(args)

    if "runner" not in args:
        parser.print_help()
    else:
        try:
            runner = args.runner(args)
            response = runner.run()
            print(response)
        except Exception as e:
            raise e


if __name__ == "__main__":
    client_main()
