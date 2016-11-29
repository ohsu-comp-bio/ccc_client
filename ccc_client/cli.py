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
from ccc_client import app_repo, exec_engine, dts, dcs, elastic_search

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

# Defines all the services and actions available in the CLI
services = {
    'app-repo': {
        'list-tools': app_repo.cli.list_tools,
        'get-metadata': app_repo.cli.get_metadata,
        'delete-metadata': app_repo.cli.delete_metadata,
        'update-metadata': app_repo.cli.update_metadata,
        'upload-metadata': app_repo.cli.upload_metadata,
        'upload-image': app_repo.cli.upload_image,
    },
    'exec-engine': {
        'submit': exec_engine.cli.submit,
        'status': exec_engine.cli.status,
        'metadata': exec_engine.cli.metadata,
        'outputs': exec_engine.cli.outputs,
        'query': exec_engine.cli.query,
    },
    'dts': {
        'post': dts.cli.post,
        'put': dts.cli.put,
        'get': dts.cli.get,
        'delete': dts.cli.delete,
        'infer-cccId': dts.cli.infer_cccid,
        'query': dts.cli.query,
    },
    'dcs': {
        'create-link': dcs.cli.create_link,
        'find-common-sets': dcs.cli.find_common_sets,
        'list-sets': dcs.cli.list_sets,
        'list-resources': dcs.cli.list_resources,
        'delete-link': dcs.cli.delete_link,
        'delete-set': dcs.cli.delete_set,
    },
    'elastic-search': {
        'query': elastic_search.cli.query,
        'publish-batch': elastic_search.cli.publish_batch,
        'publish-resource': elastic_search.cli.publish_resource,
    },
}

common_parser = argparse.ArgumentParser()
common_parser.add_argument(
    "--debug",
    default=False,
    action="store_true",
    help="debug flag"
)
common_parser.add_argument(
    "--host",
    type=str,
    help="host"
)
common_parser.add_argument(
    "--port",
    type=str,
    help="port"
)
common_parser.add_argument(
    "--authToken", "-T",
    type=str,
    help="authorization token"
)

parser = argparse.ArgumentParser(description="CCC client")
parser.add_argument("--help-long",
                    default=False,
                    action="store_true",
                    help="Show help message for all services and actions")
parser.add_argument("--version", action='version',
                    version=str(ccc_client.__version__))


# Set up the subparsers for services and actions based on the "services" dict above
services_subparsers = parser.add_subparsers(title='service', dest='service')
for service_name, actions in services.items():
    service_parser = services_subparsers.add_parser(
        service_name,
        conflict_handler='resolve'
    )
    actions_subparsers = service_parser.add_subparsers(title='action', dest='action')
    for action_name, action_module in actions.items():
        actions_subparsers.add_parser(
            action_name,
            parents=[action_module.parser, common_parser],
            conflict_handler='resolve'
        )

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


def cli_main():

    if len(sys.argv) == 1:
        return parser.print_help()

    if "--help-long" in sys.argv[1:]:
        print(display_help(parser))
        return

    args = parser.parse_args()

    if args.debug:
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if not args.runner:
        # If you're here, you probably forgot to add something like:
        #   parser.set_defaults(runner=run)
        # Look at the other CLI modules for an example.
        raise Exception("No CLI runner found.")

    args.runner(args)
