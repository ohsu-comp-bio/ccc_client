# api/workflows/v1/
#from ccc_client.cli import ArgumentParser
from argparse import ArgumentParser

def run(args):
    print 'submit', args
    #r = runner.submit_workflow(args.wdlSource,
                               #args.workflowInputs,
                               #args.workflowOptions)

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
