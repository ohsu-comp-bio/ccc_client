import argparse
from ccc_client.dts.DtsRunner import DtsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DtsRunner(args.host, args.port, args.authToken)
    r = runner.put(args.cccId, args.filepath, args.site, args.user)
    print_API_response(r)
    

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--filepath", "-f",
    required=True,
    type=str,
    help="filepath"
)
parser.add_argument(
    "--user", "-u",
    required=False,
    type=str,
    help="site user"
)
parser.add_argument(
    "--site", "-s",
    required=True,
    type=str,
    nargs="+",
    choices=["central", "dfci", "ohsu", "oicr"],
    help="site the data resides at"
)
parser.add_argument(
    "--cccId", "-i",
    required=True,
    type=str,
    help="cccId entry to update"
)
