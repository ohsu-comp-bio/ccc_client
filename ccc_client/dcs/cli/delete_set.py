import argparse
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DcsRunner(args.host, args.port, args.authToken)
    for i in args.setId:
        r = runner.delete_set(i)
        print_API_response(r)
    

parser = argparse.ArgumentParser(
    description='Remove a UUID corresponding to a set from the DCS'
)
parser.set_defaults(runner=run)
parser.add_argument(
    'setId',
    type=str,
    nargs="+",
    help='UUID(s) of resource set(s) to delete'
)
