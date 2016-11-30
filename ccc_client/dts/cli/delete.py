import argparse

from ccc_client.dts.DtsRunner import DtsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DtsRunner(args.host, args.port, args.authToken)
    for i in args.cccId:
        r = runner.delete(i)
        print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "cccId",
    type=str,
    nargs="+",
    help="cccId entry to DELETE"
)
