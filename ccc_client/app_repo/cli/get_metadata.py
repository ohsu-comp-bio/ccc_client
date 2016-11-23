# api/v1/tool/<uuid>
# api/v1/tool/<tool_name>/data
import argparse

def run(args):
    r = runner.get_metadata(args.imageIdOrName)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "imageIdOrName",
    type=str,
    help="docker image id or name"
)
