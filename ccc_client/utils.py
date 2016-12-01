from __future__ import print_function

import glob
import os
import re
import sys


def print_API_response(r):
    if r.status_code // 100 == 2:
        print(r.text)
    else:
        m = "[STATUS CODE - {0}] {1}"
        m = m.format(r.status_code, r.text)
        print(m, file=sys.stderr)


def parseAuthToken(authToken):
    if isinstance(authToken, str):
        # if the authToken matches a filepath, read the file and use this
        if re.match("^/|^\./|^\.\./", authToken):
            with open(authToken) as myfile:
                ret = "".join(line.rstrip() for line in myfile)
                return ret
        # otherwise, use authToken as is
        else:
            return authToken
    else:
        raise TypeError("authToken must be a str or valid filepath")


def resolve_filepath_from_pattern(patterns):
    if isinstance(patterns, str):
        patterns = [patterns]
    else:
        assert isinstance(patterns, list) is True

    res = []
    for file_pattern in patterns:
        file_list = glob.glob(os.path.abspath(file_pattern))
        if file_list == []:
            print("glob on", file_pattern, "did not return any files",
                  file=sys.stderr)
            raise ValueError
        else:
            res += file_list
    return res
