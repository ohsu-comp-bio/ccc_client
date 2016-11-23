import argparse

def run(args):
    r = runner.delete_metadata(args.imageId)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "imageId",
    type=str,
    help="docker image id"
)
