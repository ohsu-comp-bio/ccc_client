import argparse

from ccc_client.eve_mongo.EveMongoRunner import EveMongoRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = EveMongoRunner(args.host, args.port, args.authToken)
    r = runner.get_status()
    print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
