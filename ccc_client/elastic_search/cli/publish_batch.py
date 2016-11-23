from __future__ import print_function
import argparse
from ccc_client.elastic_search.ElasticSearchRunner import ElasticSearchRunner

def run(args):
    runner = ElasticSearchRunner(args.host, args.port, args.authToken)
    r = runner.publish_batch(
        args.tsv,
        args.site,
        args.user,
        args.project,
        args.domain,
        args.isMock,
        args.skipDtsRegistration
    )
    print(r)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--tsv", "-t",
    type=str,
    required=True,
    help="input tab delimited file"
)
parser.add_argument(
    "--site", "-s",
    type=str,
    choices=["central", "dfci", "ohsu", "oicr"],
    help="site this data is associated with"
)
parser.add_argument(
    "--user", "-u",
    type=str,
    help="user identity"
)
parser.add_argument(
    "--project", "-p",
    type=str,
    help="The project this data is associated with"
)
parser.add_argument(
    "--domain", "-d",
    type=str,
    choices=["patient", "specimen", "sample", "resource"],
    help="target domain to register the data to"
)
parser.add_argument(
    "--domainJson", "-D",
    type=str,
    help="this is the path to an alternate file describing the \
    domains/fields to use for import."
)
parser.add_argument(
    "--mock",
    dest="isMock",
    action="store_true",
    help="perform a mock operation, which runs your input through the \
    normal code path, but outputs the JSON that would otherwise be posted \
    to elasticsearch, without actually sending it"
)
parser.add_argument(
    "--skipDtsRegistration",
    dest="skipDtsRegistration",
    action="store_true",
    help="skip any attempt to register or validate CCC Ids and filepaths \
    with the DTS"
)
