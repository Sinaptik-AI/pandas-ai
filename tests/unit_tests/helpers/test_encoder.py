import unittest

import numpy as np

from pandasai.helpers.encoder import CustomEncoder


class TestCustomEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = CustomEncoder()

    def test_numpy_integer_encoding(self):
        # Test encoding of numpy integers
        data = {"value": np.int64(42)}
        expected_result = '{"value": 42}'
        self.assertEqual(self.encoder.encode(data), expected_result)

    def test_other_types_encoding(self):
        data = {"value": "test"}
        expected_result = '{"value": "test"}'
        self.assertEqual(self.encoder.encode(data), expected_result)

    def test_numpy_integer_encoding_2(self):
        # Test encoding of numpy integers
        data = {"value": 42}
        expected_result = '{"value": 42}'
        self.assertEqual(self.encoder.encode(data), expected_result)
