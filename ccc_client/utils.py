import os


def parseAuthToken(authToken):
    # if the authToken matches a filepath, read the file and use this
    if os.path.isfile(authToken):
        with open(authToken) as myfile:
            ret = "".join(line.rstrip() for line in myfile)
            return ret
    else:
        # otherwise, use authToken as is
        return authToken
