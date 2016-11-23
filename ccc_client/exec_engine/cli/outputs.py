# api/workflows/v1/<uuid>/outputs
import argparse

def run(args):
    print 'outputs', args
    return

    responses = []
    for workflowId in args.workflowId:
        r = runner.get_outputs(workflowId)
        responses.append(r)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "workflowId",
    type=str,
    nargs="+",
    help="workflow uuid"
)
