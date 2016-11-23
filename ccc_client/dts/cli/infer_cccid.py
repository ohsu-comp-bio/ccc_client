import argparse
from ccc_client.dts.DtsRunner import DtsRunner


def run(args):
    runner = DtsRunner(args.host, args.port, args.authToken)
    file_list = resolve_filepath_from_pattern(args.filepath)
    for file_iter in file_list:
        cccId = runner.infer_cccId(file_iter, args.strategy)
        print("{0}\t{1}".format(file_iter, cccId))
    

parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "filepath",
    type=str,
    nargs="+",
    help="name of file(s) or pattern to glob on"
)
parser.add_argument(
    "--strategy", "-s",
    type=str,
    default="SHA-1",
    choices=["MD5", "SHA-1"],
    help="hashing strategy to use to generate the cccId (default: SHA-1)"
)
