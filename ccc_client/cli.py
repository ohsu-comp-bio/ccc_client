"""
Command line utility for interacting with CCC services.
"""
from __future__ import print_function

import argparse
import glob
import logging
import os
import re
import sys
import ccc_client

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


def display_help(parser):
    """
    This function is called to provide an extended help message
    """
    help_msg = []
    # Print main help message
    help_msg.append(parser.format_help())

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
            help_msg.append("=" * 60)
            help_msg.append("{0}".format(choice))
            help_msg.append("=" * 60)
            help_msg.append(
                find_options(subparser.format_help(),
                             show_usage=True,
                             strip_n=1)
            )

            # Iterate through the actions for a service
            for method_subparser_action in method_subparser_actions:
                for method_choice, method_subparser in method_subparser_action.choices.items():
                    # Print service action help
                    help_msg.append("-" * len("| {0} |".format(method_choice)))
                    help_msg.append("| {0} |".format(method_choice))
                    help_msg.append("-" * len("| {0} |".format(method_choice)))
                    help_msg.append(
                        find_options(
                            method_subparser.format_help(),
                            show_usage=True,
                            strip_n=6
                        )
                    )
    return "\n".join(help_msg)


def find_options(helptext, show_usage=True, strip_n=0):
    """
    Return a substring with the optional arguments
    """
    helplist = helptext.split("\n")
    try:
        positional_arg_index = helplist.index("positional arguments:")
    except ValueError:
        positional_arg_index = None
    arg_index = helplist.index("optional arguments:")

    if not show_usage:
        if positional_arg_index:
            helplist = helplist[positional_arg_index:]
        else:
            helplist = helplist[arg_index:]
        arg_index = helplist.index("optional arguments:")

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
    common_parser.add_argument("--authToken", "-T",
                               type=str,
                               help="authorization token")

    # Main parser
    parser = argparse.ArgumentParser(description="CCC client",
                                     parents=[common_parser])
    parser.add_argument("--help-long",
                        default=False,
                        action="store_true",
                        help="Show help message for all services and actions")
    parser.add_argument("--version", action='version',
                        version=str(ccc_client.__version__))
    subparsers = parser.add_subparsers(title="service", dest="service")

    # ------------------------
    # DCS Options
    # ------------------------
    dcs = subparsers.add_parser("dcs")
    dcs.set_defaults(runner=ccc_client.DcsRunner)

    dcs_sub = dcs.add_subparsers(title="action", dest="action")

    #
    dcs_create_link = dcs_sub.add_parser(
        'create-link',
        parents=[common_parser],
        help='Assign one or more resources to a set'
    )
    dcs_create_link.add_argument('--setId', '-p',
                                 required=True,
                                 type=str,
                                 help='CCC_ID of new or existing set')
    dcs_create_link.add_argument('--cccId', '-c',
                                 type=str,
                                 nargs='+',
                                 help='CCC_ID(s) of data to be assigned to set')

    #
    dcs_comon_sets = dcs_sub.add_parser(
        'find-common-sets',
        parents=[common_parser],
        help='Find common resource sets given a list of CCC_IDs'
    )
    dcs_comon_sets.add_argument('cccId',
                                type=str,
                                nargs='+',
                                help='CCC_IDs to search')

    #
    dcs_list_sets = dcs_sub.add_parser(
        'list-sets',
        parents=[common_parser],
        help='List all sets containing a resource'
    )
    dcs_list_sets.add_argument('cccId',
                               type=str,
                               help='CCC_ID of resource')

    #
    dcs_list_resources = dcs_sub.add_parser(
        'list-resources',
        parents=[common_parser],
        help='List all resources belonging to a set'
    )
    dcs_list_resources.add_argument('setId',
                                    type=str,
                                    help='UUID of resource set')

    #
    dcs_delete_link = dcs_sub.add_parser(
        'delete-link',
        parents=[common_parser],
        help='Delete existing DCS relationship'
    )
    dcs_delete_link.add_argument('--setId', '-p',
                                 required=True,
                                 type=str,
                                 help='UUID of resource set')
    dcs_delete_link.add_argument('--cccId', '-c',
                                 type=str,
                                 nargs='+',
                                 help='CCC_DID(s) of data to be removed from set')

    #
    dcs_delete_set = dcs_sub.add_parser(
        'delete-set',
        parents=[common_parser],
        help='Remove a UUID corresponding to a set from the DCS'
    )
    dcs_delete_set.add_argument('setId',
                                type=str,
                                nargs="+",
                                help='UUID(s) of resource set(s) to delete')

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
        help="name of file(s) and/or pattern(s) to glob on"
    )
    dts_post.add_argument(
        "--user", "-u",
        required=False,
        type=str,
        help="user identity"
    )
    dts_post.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        nargs="+",
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )
    dts_post.add_argument(
        "--cccId", "-i",
        required=False,
        default=None,
        type=str,
        help="cccId; if not given one will be generated automatically"
    )

    # api/v1/dts/file
    dts_put = dts_sub.add_parser("put", parents=[common_parser])
    dts_put.add_argument(
        "--filepath", "-f",
        required=True,
        type=str,
        help="filepath"
    )
    dts_put.add_argument(
        "--user", "-u",
        required=False,
        type=str,
        help="site user"
    )
    dts_put.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        nargs="+",
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )
    dts_put.add_argument(
        "--cccId", "-i",
        required=True,
        type=str,
        help="cccId entry to update"
    )

    # api/v1/dts/file/<uuid>
    dts_get = dts_sub.add_parser("get", parents=[common_parser])
    dts_get.add_argument(
        "cccId",
        type=str,
        nargs="+",
        help="cccId entry to GET"
    )

    # api/v1/dts/file/<uuid>
    dts_delete = dts_sub.add_parser("delete", parents=[common_parser])
    dts_delete.add_argument(
        "cccId",
        type=str,
        nargs="+",
        help="cccId entry to DELETE"
    )

    # api/v1/dts/file/query?
    dts_query = dts_sub.add_parser("query", parents=[common_parser])
    dts_query.add_argument(
        "filepath",
        type=str,
        nargs="+",
        help="name of file(s) and/or pattern(s) to glob on"
    )
    dts_query.add_argument(
        "--site", "-s",
        required=True,
        type=str,
        choices=["central", "dfci", "ohsu", "oicr"],
        help="site the data resides at"
    )
    # dts_query.add_argument(
    #     "query_terms",
    #     type=str,
    #     nargs="+",
    #     help="The search terms on which to query. Can be specified multiple \
    #     times. Should be supplied in the form 'FieldName:Term'"
    # )

    # no endpoint; doesnt hit the service
    dts_infer = dts_sub.add_parser("infer-cccId", parents=[common_parser])
    dts_infer.add_argument(
        "filepath",
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
        "--imageBlob", "-b",
        type=str,
        help="name of file or path"
    )
    ar_post.add_argument(
        "--imageName", "-n",
        type=str,
        help="name of docker image"
    )
    ar_post.add_argument(
        "--imageTag", "-t",
        type=str,
        default="latest",
        help="docker image version tag"
    )
    ar_post.add_argument(
        "--metadata", "-m", type=str,
        help="tool metadata; can be a filepath or json string"
    )

    # api/v1/tool/<uuid>
    ar_put = ar_sub.add_parser("put", parents=[common_parser])
    ar_put.add_argument(
        "--metadata", "-m",
        type=str,
        required=True,
        help="tool metadata"
    )
    ar_put.add_argument(
        "--imageId", "-i",
        type=str,
        help="docker image id"
    )

    # api/v1/tool/<uuid>
    # api/v1/tool/<tool_name>/data
    ar_get = ar_sub.add_parser("get", parents=[common_parser])
    ar_get.add_argument(
        "imageIdOrName",
        type=str,
        help="docker image id or name"
    )

    # api/v1/tool/<uuid>
    ar_delete = ar_sub.add_parser("delete", parents=[common_parser])
    ar_delete.add_argument(
        "imageId",
        type=str,
        help="docker image id"
    )

    # v2/_catalog
    ar_list_tools = ar_sub.add_parser("list-tools", parents=[common_parser])

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
        required=True,
        help="WDL source file defining a workflow"
    )
    ee_post.add_argument(
        "--workflowInputs", "-i",
        type=str,
        nargs="+",
        required=True,
        help="json file(s) defining workflow input mappings"
    )
    ee_post.add_argument(
        "--workflowOptions", "-o",
        type=str,
        default="-",
        help="workflow options"
    )

    # api/workflows/v1/query?
    ee_query = ee_sub.add_parser("query", parents=[common_parser])
    ee_query.add_argument(
        "query_terms",
        type=str,
        nargs="+",
        help="The search terms on which to query. Can be specified multiple \
        times. Should be supplied in the form 'FieldName:Term'. Possible field \
        names: name, id, status, start, end, page, pagesize"
    )

    # api/workflows/v1/<uuid>/status
    ee_status = ee_sub.add_parser("status", parents=[common_parser])
    ee_status.add_argument(
        "workflowId",
        type=str,
        nargs="+",
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/outputs
    ee_outputs = ee_sub.add_parser("outputs", parents=[common_parser])
    ee_outputs.add_argument(
        "workflowId",
        type=str,
        nargs="+",
        help="workflow uuid"
    )

    # api/workflows/v1/<uuid>/metadata
    ee_meta = ee_sub.add_parser("metadata", parents=[common_parser])
    ee_meta.add_argument(
        "workflowId",
        type=str,
        nargs="+",
        help="workflow uuid"
    )

    # ------------------------
    # Elastic Search Options
    # ------------------------
    es = subparsers.add_parser("elasticsearch")
    es.set_defaults(runner=ccc_client.ElasticSearchRunner)

    es_sub = es.add_subparsers(title="action", dest="action")

    es_query = es_sub.add_parser("query", parents=[common_parser])
    es_query.add_argument(
        "--domain", "-d",
        type=str,
        choices=["patient", "specimen", "sample", "resource"],
        help="target domain of query"
    )
    es_query.add_argument(
        "--query-terms", "-q",
        type=str,
        required=True,
        nargs="+",
        help="The search terms on which to query. Can be specified multiple \
        times. Should be supplied in the form 'FieldName:Term'"
    )

    es_publish_batch = es_sub.add_parser("publish-batch",
                                         parents=[common_parser])
    es_publish_batch.add_argument(
        "--tsv", "-t",
        type=str,
        required=True,
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
    es_publish_batch.add_argument(
        "--domainJson", "-D",
        type=str,
        help="this is the path to an alternate file describing the \
        domains/fields to use for import."
    )
    es_publish_batch.add_argument(
        "--mock",
        dest="isMock",
        action="store_true",
        help="perform a mock operation, which runs your input through the \
        normal code path, but outputs the JSON that would otherwise be posted \
        to elasticsearch, without actually sending it"
    )
    es_publish_batch.add_argument(
        "--skipDtsRegistration",
        dest="skipDtsRegistration",
        action="store_true",
        help="skip any attempt to register or validate CCC Ids and filepaths \
        with the DTS"
    )

    es_publish_resource = es_sub.add_parser("publish-resource",
                                            parents=[common_parser])
    es_publish_resource.add_argument(
        "--filepath", "-f",
        type=str,
        required=True,
        help="file to be registered in ES index"
    )
    es_publish_resource.add_argument(
        "--mimeType", "-t",
        type=str,
        help="the MIME type of the file"
    )
    es_publish_resource.add_argument(
        "--inheritFrom", "-i",
        type=str,
        help="a cccId - if provided, the fields of this existing record will \
        be queried and applied to the incoming resource. Any values provided \
        using --propertyOverride will override these"
    )
    es_publish_resource.add_argument(
        "--propertyOverride", "-o",
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
    es_publish_resource.add_argument(
        "--domainJson", "-D",
        type=str,
        help="this is the path to an alternate file describing the \
        domains/fields to use for import."
    )
    es_publish_resource.add_argument(
        "--mock",
        dest="isMock",
        action="store_true",
        help="perform a mock operation, which runs your input through the \
        normal code path, but outputs the JSON that would otherwise be posted \
        to elasticsearch, without actually sending it"
    )
    es_publish_resource.add_argument(
        "--skipDtsRegistration",
        dest="skipDtsRegistration",
        action="store_true",
        help="skip any attempt to register or validate CCC Ids and filepaths \
        with the DTS"
    )
    return parser


def resolve_filepath_from_pattern(patterns):
    if isinstance(patterns, str):
        patterns = [patterns]
    else:
        assert isinstance(patterns, list) is True

    res = []
    for file_pattern in patterns:
        file_list = glob.glob(os.path.abspath(file_pattern))
        if file_list == []:
            print("glob on", file_pattern, "did not return any files",
                  file=sys.stderr)
            raise ValueError
        else:
            res += file_list
    return res


def cli_main():
    parser = setup_parser()

    if len(sys.argv) == 1:
        return parser.print_help()

    if "--help-long" in sys.argv[1:]:
        print(display_help(parser))
        return

    args = parser.parse_args()

    if "runner" not in args:
        parser.print_help()
        raise RuntimeError()

    runner = args.runner(host=args.host,
                         port=args.port,
                         authToken=args.authToken)
    responses = []

    if args.debug:
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    # ------------------------
    # DCS
    # ------------------------
    if args.service == "dcs":
        if args.action == "create-link":
            for i in args.cccId:
                r = runner.create_link(args.setId, i)
                responses.append(r)
        elif args.action == "find-common-sets":
            r = runner.find_common_sets(args.ids)
            responses.append(r)
        elif args.action == "list-sets":
            r = runner.list_all_sets(args.cccId)
            responses.append(r)
        elif args.action == "list-resources":
            r = runner.list_all_resources(args.setId)
            responses.append(r)
        elif args.action == "delete-link":
            for i in args.cccId:
                r = runner.delete_link(args.setId, i)
                responses.append(r)
        elif args.action == "delete-set":
            for i in args.setId:
                r = runner.delete_set(i)
                responses.append(r)
        else:
            raise NotImplementedError

    # ------------------------
    # DTS
    # ------------------------
    if args.service == "dts":
        if args.action == "post":
            file_list = resolve_filepath_from_pattern(args.filepath)
            for file_iter in file_list:
                r = runner.post(file_iter, args.site,
                                args.user, args.cccId)
                responses.append(r)
                if r.status_code // 100 == 2:
                    print("{0}\t{1}".format(file_iter, r.text))
        elif args.action == "put":
            r = runner.put(args.cccId, args.filepath, args.site, args.user)
            responses.append(r)
        elif args.action == "get":
            for cccId in args.cccId:
                r = runner.get(cccId)
                responses.append(r)
        elif args.action == "delete":
            for cccId in args.cccId:
                r = runner.delete(cccId)
                responses.append(r)
        elif args.action == "query":
            file_list = resolve_filepath_from_pattern(args.filepath)
            for file_iter in file_list:
                r = runner.query(file_iter, args.site)
                responses.append(r)
        elif args.action == "infer-cccId":
            file_list = resolve_filepath_from_pattern(args.filepath)
            for file_iter in file_list:
                cccId = runner.infer_cccId(file_iter, args.strategy)
                print("{0}\t{1}".format(file_iter, cccId))
            return
        else:
            raise NotImplementedError

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
        elif args.action == "get":
            r = runner.get(args.imageIdOrName)
            responses.append(r)
        elif args.action == "delete":
            r = runner.delete(args.imageId)
            responses.append(r)
        elif args.action == "list-tools":
            r = runner.list_tools()
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
        elif args.action == "query":
            r = runner.query(args.query_terms)
            responses.append(r)
        else:
            for workflowId in args.workflowId:
                if args.action == "status":
                    r = runner.get_status(workflowId)
                    responses.append(r)
                elif args.action == "metadata":
                    r = runner.get_metadata(workflowId)
                    responses.append(r)
                elif args.action == "outputs":
                    r = runner.get_outputs(workflowId)
                    responses.append(r)
                else:
                    raise NotImplementedError

    # ------------------------
    # Elastic Search
    # ------------------------
    elif args.service == "elasticsearch":
        if args.domainJson:
            runner.setDomainDescriptors(args.domainJson)
        if args.action == "query":
            r = runner.query(args.domain,
                             args.query_terms)
        elif args.action == "publish-batch":
            r = runner.publish_batch(args.tsv,
                                     args.site,
                                     args.user,
                                     args.project,
                                     args.domain,
                                     args.isMock,
                                     args.skipDtsRegistration)
        elif args.action == "publish-resource":
            r = runner.publish_resource(args.filepath,
                                        args.site,
                                        args.user,
                                        args.project,
                                        args.workflowId,
                                        args.mimeType,
                                        'resource',
                                        args.inheritFrom,
                                        args.property_override,
                                        args.isMock,
                                        args.skipDtsRegistration)
        else:
            raise NotImplementedError
        print(r)

    else:
        raise NotImplementedError

    # ------------------------
    # Response Handling
    # ------------------------
    for r in responses:
        if r.status_code // 100 == 2:
            if not (args.service == "dts" and args.action == "post"):
                print(r.text)
        else:
            print("[STATUS CODE - {0}] {1}".format(r.status_code, r.text),
                  file=sys.stderr)
