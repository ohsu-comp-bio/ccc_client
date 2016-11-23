# api/workflows/v1/query?
import argparse

def run(args):
    print 'query', args
    return 

    r = runner.query(args.query_terms)

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
