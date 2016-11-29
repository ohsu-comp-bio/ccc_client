# api/workflows/v1/
from argparse import ArgumentParser
from ccc_client.exec_engine.ExecEngineRunner import ExecEngineRunner
from ccc_client.utils import print_API_response

def run(args):
    runner = ExecEngineRunner(args.host, args.port, args.authToken)
    r = runner.submit_workflow(
        args.wdlSource,
        args.workflowInputs,
        args.workflowOptions
    )
    print_API_response(r)

parser = ArgumentParser()
parser.set_defaults(runner=run)

parser.add_argument(
    "--wdlSource", "-s",
    type=str,
    required=True,
    help="WDL source file defining a workflow"
)
parser.add_argument(
    "--workflowInputs", "-i",
    type=str,
    nargs="+",
    required=True,
    help="json file(s) defining workflow input mappings"
)
parser.add_argument(
    "--workflowOptions", "-o",
    type=str,
    default="-",
    help="workflow options"
)
