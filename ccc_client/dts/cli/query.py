import argparse
from ccc_client.dts.DtsRunner import DtsRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = DtsRunner(args.host, args.port, args.authToken)
    file_list = resolve_filepath_from_pattern(args.filepath)
    for file_iter in file_list:
        r = runner.query(file_iter, args.site)
        print_API_response(r)
    

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "filepath",
    type=str,
    nargs="+",
    help="name of file(s) and/or pattern(s) to glob on"
)
parser.add_argument(
    "--site", "-s",
    required=True,
    type=str,
    choices=["central", "dfci", "ohsu", "oicr"],
    help="site the data resides at"
)
parser.add_argument(
    "query_terms",
    type=str,
    nargs="+",
    help="The search terms on which to query. Can be specified multiple times. Should be supplied in the form 'FieldName:Term'"
)
