"""
Command line utility for interacting with CCC services.
"""
from __future__ import print_function

import argparse
import sys

import ccc_client
from ccc_service_runners import DtsRunner, AppRepoRunner, ExecEngineRunner


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
    parser.add_argument("--version", action='version',
                        version=str(ccc_client.__version__))
    parser.add_argument("--debug",
                        default=False,
                        action="store_true",
                        help="debug flag")
    parser.add_argument("--help-long",
                        default=False,
                        action="store_true",
                        help="Show help message for all services and actions")

    subparsers = parser.add_subparsers(title="service", dest="service")

    # ------------------------
    # DTS Options
    # ------------------------
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

    # ------------------------
    # App Repo Options
    # ------------------------
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
        "--imageBlob", "-b", type=str, help="name of file or path"
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

    # ------------------------
    # Exec Engine Options
    # ------------------------
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


def client_main():
    parser = setup_parser()

    if "--help-long" in sys.argv[1:]:
        return display_help(parser)

    args = parser.parse_args()

    if "runner" not in args:
        parser.print_help()
        raise RuntimeError()

    runner = args.runner(args)
    responses = []

    # ------------------------
    # DTS
    # ------------------------
    if args.service == "dts":
        if args.action == "post":
            for f in args.filepath:
                r = runner.post(f, args.site, args.user)
                responses.append(r)
        elif args.action == "get":
            for cccId in args.cccId:
                r = runner.get(cccId)
                responses.append(r)
        elif args.action == "delete":
            for cccId in args.cccId:
                r = runner.delete(cccId)
                responses.append(r)

    # ------------------------
    # App Repo
    # ------------------------
    elif args.service == "app-repo":
        if args.action == "post":
            r = runner.post(args.imageBlob, args.imageName, args.imageTag)
            responses.append(r)
            imageId = re.compile(
                r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}').findall(
                    r.content)[0]
            if args.metadata is not None:
                r = runner.put(imageId, args.metadata)
                responses.append(r)
        elif args.action == "put":
            r = runner.put(args.imageId, args.metadata)
            responses.append(r)
        elif args.action == "delete":
            r = runner.delete(args.imageId)
            responses.append(r)

    # ------------------------
    # Exec Engine
    # ------------------------
    elif args.service == "exec-engine":
        if args.action == "submit":
            r = runner.submit_workflow(args.wdlSource,
                                       args.workflowInputs,
                                       args.workflowOptions)
            responses.append(r)
        elif args.action == "status":
            r = runner.get_status(args.workflowId)
            responses.append(r)
        elif args.action == "metadata":
            r = runner.get_metadata(args.workflowId)
            responses.append(r)
        elif args.action == "outputs":
            r = runner.get_outputs(args.workflowId)
            responses.append(r)

    # ------------------------
    # Response Handling
    # ------------------------
    for r in responses:
        if args.debug:
            print(r.headers)
        if r.status_code // 100 == 2:
            if not (args.service == "dts" and args.action == "post"):
                print(r.text)
            else:
                sys.stderr.write("[STATUS CODE - {0}]    {1}\n".format(
                    r.status_code, r.text))
