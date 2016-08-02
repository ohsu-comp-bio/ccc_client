import re


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
