import unittest
import os
from pandasai.callbacks.file import FileCallback


class TestFileCallback(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.abspath("test_file.txt")
        self.callback = FileCallback(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_on_code(self):
        response = "Hello, world!"
        self.callback.on_code(response)
        with open(self.filename, "r") as f:
            contents = f.read()
        self.assertEqual(contents, response)
