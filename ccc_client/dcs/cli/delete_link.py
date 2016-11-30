import argparse

from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    for i in args.cccId:
        r = runner.delete_link(args.setId, i)
        print_API_response(r)


parser = argparse.ArgumentParser(
    description='Delete existing DCS relationship'
)
parser.set_defaults(runner=run)
parser.add_argument(
    '--setId', '-p',
    required=True,
    type=str,
    help='UUID of resource set'
)
parser.add_argument(
    '--cccId', '-c',
    type=str,
    nargs='+',
    help='CCC_DID(s) of data to be removed from set'
)
