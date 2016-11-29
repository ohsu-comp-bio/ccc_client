# api/workflows/v1/query?
import argparse
from ccc_client.exec_engine.ExecEngineRunner import ExecEngineRunner
from ccc_client.utils import print_API_response

def run(args):
    runner = ExecEngineRunner(args.host, args.port, args.authToken)
    r = runner.query(args.query_terms)
    print_API_response(r)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "query_terms",
    type=str,
    nargs="+",
    help="The search terms on which to query. Can be specified multiple \
    times. Should be supplied in the form 'FieldName:Term'. Possible field \
    names: name, id, status, start, end, page, pagesize"
)
