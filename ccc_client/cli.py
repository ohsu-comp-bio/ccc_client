"""
Command line utility for interacting with CCC services.
"""
from __future__ import print_function

import argparse
import re
import sys

import ccc_client
from es_runner import ElasticSearchRunner


def display_help(parser):
    """
    This function is called to provide an extended help message
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
            print(find_options(subparser.format_help(), strip_n=1))

            # Iterate through the actions for a service
            for method_subparser_action in method_subparser_actions:
                for method_choice, method_subparser in method_subparser_action.choices.items():
                    # Print service action help
                    print("-" * len("| {0} |".format(method_choice)))
                    print("| {0} |".format(method_choice))
                    print("-" * len("| {0} |".format(method_choice)))
                    print(find_options(method_subparser.format_help(), strip_n=4))


def find_options(helptext, show_usage=True, strip_n=0):
    """
    Return a substring with the optional arguments
    """
    helplist = helptext.split("\n")

    arg_index = helplist.index("optional arguments:")

    # Remove usage info
    if not show_usage:
        helplist = helplist[arg_index:]

    # Remove help flag info
    del helplist[(arg_index + 1):(arg_index + 1 + strip_n)]

    # Handle cases where there are no optional arguments
    if helplist[arg_index + 1] == "":
        del helplist[arg_index + 1]
        del helplist[arg_index]

    return "\n".join(helplist)


def setup_parser():
    # Options shared among all subparsers
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

    # Main parser
    parser = argparse.ArgumentParser(description="CCC client", parents=[common_parser])
    parser.add_argument("--help-long",
                        default=False,
                        action="store_true",
                        help="Show help message for all services and actions")
    parser.add_argument("--version", action='version',
                        version=str(ccc_client.__version__))
    subparsers = parser.add_subparsers(title="service", dest="service")

    # ------------------------
    # DTS Options
    # ------------------------
    dts = subparsers.add_parser("dts")
    dts.set_defaults(runner=ccc_client.DtsRunner)

    dts_sub = dts.add_subparsers(title="action", dest="action")

    # api/v1/dts/file
    dts_post = dts_sub.add_parser("post", parents=[common_parser])
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
        help="user identity")
    dts_post.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )

    # api/v1/dts/file
    dts_put = dts_sub.add_parser("put", parents=[common_parser])
    dts_put.add_argument(
        "--filepath", "-f",
        required=True,
        type=str,
        nargs="+",
        help="name of file(s) or pattern to glob on"
    )
    dts_put.add_argument(
        "--user", "-u",
        required=True,
        type=str,
        help="site user")
    dts_put.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )

    # api/v1/dts/file/<uuid>
    dts_get = dts_sub.add_parser("get", parents=[common_parser])
    dts_get.add_argument(
        "--cccId",
        required=True,
        type=str,
        nargs="+",
        help="cccId entry to GET"
    )

    # api/v1/dts/file/<uuid>
    dts_delete = dts_sub.add_parser("delete", parents=[common_parser])
    dts_delete.add_argument(
        "--cccId",
        required=True,
        type=str,
        nargs="+",
        help="cccId entry to DELETE"
    )

    dts_infer = dts_sub.add_parser("infer-cccId", parents=[common_parser])
    dts_infer.add_argument(
        "--filepath", "-f",
        required=True,
        type=str,
        nargs="+",
        help="name of file(s) or pattern to glob on"
    )
    dts_infer.add_argument(
        "--strategy", "-s",
        type=str,
        default="SHA-1",
        choices=["MD5", "SHA-1"],
        help="hashing strategy to use to generate the cccId (default: SHA-1)"
    )

    # ------------------------
    # App Repo Options
    # ------------------------
    ar = subparsers.add_parser("app-repo")
    ar.set_defaults(runner=ccc_client.AppRepoRunner)

    ar_sub = ar.add_subparsers(title="action", dest="action")

    # api/v1/tool/
    ar_post = ar_sub.add_parser("post", parents=[common_parser])
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
        help="tool metadata; can be a filepath or json string"
    )

    # api/v1/tool/<uuid>
    ar_put = ar_sub.add_parser("put", parents=[common_parser])
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
    ar_get = ar_sub.add_parser("get", parents=[common_parser])
    ar_get.add_argument(
        "--imageId", "-i", type=str,
        help="docker image id"
    )

    # api/v1/tool/<uuid>
    ar_delete = ar_sub.add_parser("delete", parents=[common_parser])
    ar_delete.add_argument(
        "--imageId", "-i", type=str,
        help="docker image id"
    )

    # ------------------------
    # Exec Engine Options
    # ------------------------
    ee = subparsers.add_parser("exec-engine")
    ee.set_defaults(runner=ccc_client.ExecEngineRunner)

    ee_sub = ee.add_subparsers(title="action", dest="action")

    # api/workflows/v1/
    ee_post = ee_sub.add_parser("submit", parents=[common_parser])
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
    ee_status = ee_sub.add_parser("status", parents=[common_parser])
    ee_status.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/outputs
    ee_outputs = ee_sub.add_parser("outputs", parents=[common_parser])
    ee_outputs.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/metadata
    ee_meta = ee_sub.add_parser("metadata", parents=[common_parser])
    ee_meta.add_argument(
        "--workflowId", "-i",
        type=str,
        help="workflow uuid"
    )

    # ------------------------
    # Elastic Search Options
    # ------------------------
    es = subparsers.add_parser("elasticsearch")
    es.set_defaults(runner=ElasticSearchRunner)

    es_sub = es.add_subparsers(title="action", dest="action")

    es_query = es_sub.add_parser("query", parents=[common_parser])
    es_query.add_argument(
        "--token", "-T",
        type=str,
        help="auth token"
    )
    es_query.add_argument(
        "--domain", "-d",
        type=str,
        choices=["patient", "specimen", "sample", "resource"],
        help="target domain of query"
    )
    es_query.add_argument(
        "--query-terms", "-q",
        type=str,
        nargs="+",
        help="The search terms on which to query. Can be specified multiple \
        times. Should be supplied in the form 'FieldName:Term'"
    )

    es_publish_batch = es_sub.add_parser("publish-batch",
                                         parents=[common_parser])
    es_publish_batch.add_argument(
        "--token", "-T",
        type=str,
        help="auth token"
    )
    es_publish_batch.add_argument(
        "--tsv", "-t",
        type=str,
        help="input tab delimited file"
    )
    es_publish_batch.add_argument(
        "--site", "-s",
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site this data is associated with"
    )
    es_publish_batch.add_argument(
        "--user", "-u",
        type=str,
        help="user identity"
    )
    es_publish_batch.add_argument(
        "--project", "-p",
        type=str,
        help="The project this data is associated with"
    )
    es_publish_batch.add_argument(
        "--domain", "-d",
        type=str,
        choices=["patient", "specimen", "sample", "resource"],
        help="target domain to register the data to"
    )

    es_publish_resource = es_sub.add_parser("publish-resource",
                                            parents=[common_parser])
    es_publish_resource.add_argument(
        "--token", "-T",
        type=str,
        help="auth token"
    )
    es_publish_resource.add_argument(
        "--filepath", "-f",
        type=str,
        help="file to be registered in ES index"
    )
    es_publish_resource.add_argument(
        "--filetype", "-t",
        type=str,
        help="the MIME type of the file"
    )
    es_publish_resource.add_argument(
        "--inheritFrom", "-i",
        type=str,
        help="a cccId - if provided, the fields of this existing record will \
        be queried and applied to the incoming resource. Any values provided \
        using --property-override will override these"
    )
    es_publish_resource.add_argument(
        "--property-override", "-o",
        type=str,
        nargs="+",
        help="One or more fields to apply to the incoming resource. The values \
        should be supplied in the form 'FieldName:Value'"
    )
    es_publish_resource.add_argument(
        "--site", "-s",
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site this file is associated with"
    )
    es_publish_resource.add_argument(
        "--user", "-u",
        type=str,
        help="user identity"
    )
    es_publish_resource.add_argument(
        "--project", "-p",
        type=str,
        help="The project this file is associated with"
    )
    es_publish_resource.add_argument(
        "--workflowId", "-w",
        type=str,
        help="The workflow this file was generated by"
    )

    return parser


def cli_main():
    parser = setup_parser()

    if len(sys.argv) == 1:
        return parser.print_help()

    if "--help-long" in sys.argv[1:]:
        return display_help(parser)

    args = parser.parse_args()

    if "runner" not in args:
        parser.print_help()
        raise RuntimeError()

    runner = args.runner(args.host, args.port)
    responses = []

    # ------------------------
    # DTS
    # ------------------------
    if args.service == "dts":
        if args.action == "post":
            for f in args.filepath:
                r = runner.post(f, args.site, args.user)
                responses.append(r)
        elif args.action == "put":
            for f in args.filepath:
                r = runner.put(f, args.site, args.user)
                responses.append(r)
        elif args.action == "get":
            for cccId in args.cccId:
                r = runner.get(cccId)
                responses.append(r)
        elif args.action == "delete":
            for cccId in args.cccId:
                r = runner.delete(cccId)
                responses.append(r)
        elif args.action == "infer-cccId":
            for f in args.filepath:
                runner.infer_cccId(f, args.strategy)
            return None

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
    # Elastic Search
    # ------------------------
    elif args.service == "elasticsearch":
        if args.action == "query":
            r = runner.query(args.domain, args.query, args.output)
            responses.append(r)
        elif args.action == "publish-batch":
            r = runner.publish_batch(args.tsv, args.site, args.user,
                                     args.project, args.domain)
            responses.append(r)
        elif args.action == "publish-resource":
            r = runner.publish_resource(args.filepath, args.site, args.user,
                                        args.project, args.workflowId,
                                        args.filetype, 'resource',
                                        args.inheritFrom,
                                        args.property_override)
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
            sys.stderr.write("[STATUS CODE - {0}] {1}\n".format(
                r.status_code, r.text))
