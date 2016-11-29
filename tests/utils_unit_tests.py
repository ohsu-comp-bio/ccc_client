import unittest
import tempfile

from ccc_client import utils


class TestUtils(unittest.TestCase):
    authToken = "superFakeToken"

    authHeader = {
        "Authorization": " ".join(["Bearer", authToken])
    }

    authToken_file = tempfile.NamedTemporaryFile(delete=False)
    authToken_file.write(authToken.encode())
    authToken_file.close()
    authToken_path = authToken_file.name

    invalid_filepath = "/ZAfvcacADF/nonExistentToken.txt"

    def test_parseAuthToken(self):
        # pass authToken as str
        result = utils.parseAuthToken(self.authToken)
        self.assertEqual(result, self.authToken)

        # pass authToken in file
        result = utils.parseAuthToken(self.authToken_path)
        self.assertEqual(result, self.authToken)

        # try to pass auth header
        with self.assertRaises(TypeError):
            result = utils.parseAuthToken(self.authHeader)

        # pass authToken in file that doesnt exist
        with self.assertRaises(IOError):
            result = utils.parseAuthToken(self.invalid_filepath)
