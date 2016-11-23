# api/workflows/v1/<uuid>/metadata
import argparse

def run(args):
    print 'metadata', args
    return

    responses = []
    for workflowId in args.workflowId:
        r = runner.get_metadata(workflowId)
        responses.append(r)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "workflowId",
    type=str,
    nargs="+",
    help="workflow uuid"
)
