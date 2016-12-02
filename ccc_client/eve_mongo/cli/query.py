import argparse

from ccc_client.eve_mongo.EveMongoRunner import EveMongoRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = EveMongoRunner(args.host, args.port, args.authToken)
    r = runner.query(args.endpoint, args.filter)
    print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--endpoint", "-e", type=str,
    required=True,
    choices=["programs", "projects", "files"],
    help="data type to query"
)
parser.add_argument(
    "--filter", "-f", type=str,
    help='json filter for query: e.g. "{"program": "CCC"}"'
)