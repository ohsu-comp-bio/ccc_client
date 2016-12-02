import argparse

from ccc_client.eve_mongo.EveMongoRunner import EveMongoRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = EveMongoRunner(args.host, args.port, args.authToken)
    r = runner.publish(args.tsv, args.site, args.user, args.program,
                       args.project, args.domain, args.domainJson)
    for response in r:
        print_API_response(response)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--tsv", "-t", type=str,
    required=True,
    help="input tab delimited file"
)
parser.add_argument(
    "--site", "-s", type=str,
    choices=["central", "dfci", "ohsu", "oicr"],
    help="site this data is associated with"
)
parser.add_argument(
    "--user", "-u", type=str,
    help="user identity"
)
parser.add_argument(
    "--program", "-P", type=str,
    help="The program this data is associated with"
)
parser.add_argument(
    "--project", "-p", type=str,
    help="The project this data is associated with"
)
parser.add_argument(
    "--domain", "-d", type=str,
    choices=["case", "sample", "file"],
    help="target domain to register the data to"
)
parser.add_argument(
    "--domainJson", "-D", type=str,
    help="this is the path to an alternate file describing the "
         "domains/fields to use for import."
)
