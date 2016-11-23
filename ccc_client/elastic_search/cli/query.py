from __future__ import print_function
import argparse
from ccc_client.elastic_search.ElasticSearchRunner import ElasticSearchRunner

def run(args):
    runner = ElasticSearchRunner(args.host, args.port, args.authToken)
    if args.domainJson:
        runner.setDomainDescriptors(args.domainJson)
    r = runner.query(args.domain, args.query_terms)
    print(r)
    

parser = argparse.ArgumentParser()
parser.add_argument(
    "--domain", "-d",
    type=str,
    choices=["patient", "specimen", "sample", "resource"],
    help="target domain of query"
)
parser.add_argument(
    "--query-terms", "-q",
    type=str,
    required=True,
    nargs="+",
    help="The search terms on which to query. Can be specified multiple \
    times. Should be supplied in the form 'FieldName:Term'"
)
