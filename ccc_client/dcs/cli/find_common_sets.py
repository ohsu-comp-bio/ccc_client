import argparse
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    r = runner.find_common_sets(args.ids)
    print_API_response(r)
    

parser = argparse.ArgumentParser(
    description='Find common resource sets given a list of CCC_IDs'
)
parser.set_defaults(runner=run)
parser.add_argument(
    'cccId',
    type=str,
    nargs='+',
    help='CCC_IDs to search'
)
