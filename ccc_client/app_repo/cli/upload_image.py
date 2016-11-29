# api/v1/tool/
import argparse
from ccc_client.app_repo.AppRepoRunner import AppRepoRunner
from ccc_client.utils import print_API_response

def run(args):
    runner = AppRepoRunner(args.host, args.port, args.authToken)
    r = runner.upload_image(args.imageBlob, args.imageName, args.imageTag)
    print_API_response(r)

    if args.metadata is not None:
        r = runner.upload_metadata(None, args.metadata)
        print_API_response(r)

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--imageBlob", "-b",
    type=str,
    help="name of file or path"
)
parser.add_argument(
    "--imageName", "-n",
    type=str,
    help="name of docker image"
)
parser.add_argument(
    "--imageTag", "-t",
    type=str,
    default="latest",
    help="docker image version tag"
)
parser.add_argument(
    "--metadata", "-m", type=str,
    help="tool metadata; can be a filepath or json string"
)
