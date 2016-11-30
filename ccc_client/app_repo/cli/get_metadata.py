import argparse

from ccc_client.app_repo.AppRepoRunner import AppRepoRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = AppRepoRunner(args.host, args.port, args.authToken)
    r = runner.get_metadata(args.imageIdOrName)
    print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "imageIdOrName",
    type=str,
    help="docker image id or name"
)
