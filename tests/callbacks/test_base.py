import unittest
import io
from pandasai.callbacks.base import BaseCallback, StdoutCallback
from pandasai.exceptions import MethodNotImplementedError


class TestBaseCallback(unittest.TestCase):
    def setUp(self):
        self.callback = BaseCallback()

    def test_on_code(self):
        with self.assertRaises(MethodNotImplementedError):
            self.callback.on_code("response")


class TestStdoutCallback(unittest.TestCase):
    def setUp(self):
        self.callback = StdoutCallback()

    def test_on_code(self):
        response = "Hello, world!"
        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            self.callback.on_code(response)
            self.assertEqual(fake_stdout.getvalue().strip(), response)
