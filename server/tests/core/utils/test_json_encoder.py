import unittest
from unittest.mock import patch
import datetime
import json
import numpy as np
import pandas as pd
from core.utils.json_encoder import jsonable_encoder, CustomEncoder


class TestJsonableEncoder(unittest.TestCase):
    def test_encode_np_integer(self):
        data = {"value": np.int64(10)}
        expected_result = '{"value": 10}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    def test_encode_np_float(self):
        data = {"value": np.float64(3.14)}
        expected_result = '{"value": 3.14}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    def test_encode_np_array(self):
        data = {"array": np.array([1, 2, 3])}
        expected_result = '{"array": [1, 2, 3]}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    def test_encode_datetime(self):
        data = {"timestamp": datetime.datetime(2024, 6, 7, 12, 30)}
        expected_result = '{"timestamp": "2024-06-07T12:30:00"}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    def test_encode_pd_timestamp(self):
        data = {"timestamp": pd.Timestamp("2024-06-07")}
        expected_result = '{"timestamp": "2024-06-07T00:00:00"}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    def test_other_objects(self):
        data = {"name": "John", "age": 30}
        expected_result = '{"name": "John", "age": 30}'
        self.assertEqual(jsonable_encoder(data), json.loads(expected_result))

    @patch("core.utils.json_encoder.json.dumps")
    def test_custom_encoder_called(self, mock_dumps):
        data = {"value": np.int64(10)}

        mock_dumps.return_value = '{"value": 10}'

        result = jsonable_encoder(data)

        mock_dumps.assert_called_once_with(data, cls=CustomEncoder)

        self.assertEqual(result, data)


if __name__ == "__main__":
    unittest.main()
