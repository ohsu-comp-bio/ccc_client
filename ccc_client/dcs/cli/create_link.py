import argparse
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    for i in args.cccId:
        r = runner.create_link(args.setId, i)
        print_API_response(r)
    

parser = argparse.ArgumentParser(
    description='Assign one or more resources to a set'
)
parser.set_defaults(runner=run)
parser.add_argument(
    '--setId', '-p',
    required=True,
    type=str,
    help='CCC_ID of new or existing set'
)
parser.add_argument(
    '--cccId', '-c',
    type=str,
    nargs='+',
    help='CCC_ID(s) of data to be assigned to set'
)
