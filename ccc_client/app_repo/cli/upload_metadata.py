# api/v1/tool/<uuid>
import argparse

def run(args):
    r = runner.upload_metadata(args.imageId, args.metadata)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--metadata", "-m",
    type=str,
    required=True,
    help="tool metadata"
)
parser.add_argument(
    "--imageId", "-i",
    type=str,
    help="docker image id"
)
