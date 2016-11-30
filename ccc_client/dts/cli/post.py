import argparse

from ccc_client.dts.DtsRunner import DtsRunner
from ccc_client.utils import print_API_response, resolve_filepath_from_pattern


def run(args):
    runner = DtsRunner(args.host, args.port, args.authToken)
    file_list = resolve_filepath_from_pattern(args.filepath)

    for file_iter in file_list:
        r = runner.post(file_iter, args.site,
                        args.user, args.cccId)

        if r.status_code // 100 == 2:
            print("{0}\t{1}".format(file_iter, r.text))
        else:
            print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--filepath", "-f",
    required=True,
    type=str,
    nargs="+",
    help="name of file(s) and/or pattern(s) to glob on"
)
parser.add_argument(
    "--user", "-u",
    required=False,
    type=str,
    help="user identity"
)
parser.add_argument(
    "--site", "-s",
    required=True,
    type=str,
    nargs="+",
    choices=["central", "dfci", "ohsu", "oicr"],
    help="site the data resides at"
)
parser.add_argument(
    "--cccId", "-i",
    required=False,
    default=None,
    type=str,
    help="cccId; if not given one will be generated automatically"
)
