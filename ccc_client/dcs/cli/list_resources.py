import argparse
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    r = runner.list_all_resources(args.setId)
    print_API_response(r)
    

parser = argparse.ArgumentParser(
    description='List all resources belonging to a set'
)
parser.set_defaults(runner=run)
parser.add_argument(
    'setId',
    type=str,
    help='UUID of resource set'
)
