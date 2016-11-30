# api/workflows/v1/<uuid>/metadata
import argparse
from ccc_client.exec_engine.ExecEngineRunner import ExecEngineRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = ExecEngineRunner(args.host, args.port, args.authToken)
    for workflowId in args.workflowId:
        r = runner.get_metadata(workflowId)
        print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "workflowId",
    type=str,
    nargs="+",
    help="workflow uuid"
)
