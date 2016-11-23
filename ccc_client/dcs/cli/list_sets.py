import argparse
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    r = runner.list_all_sets(args.cccId)
    print_API_response(r)
    

parser = argparse.ArgumentParser(
    description='List all sets containing a resource'
)
parser.set_defaults(runner=run)
parser.add_argument(
    'cccId',
    type=str,
    help='CCC_ID of resource'
)
