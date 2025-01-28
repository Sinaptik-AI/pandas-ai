import base64
import datetime
import json
import os
import unittest
from unittest.mock import mock_open, patch

import numpy as np
import pandas as pd
from pandasai_docker.serializer import CustomEncoder, ResponseSerializer


class TestResponseSerializer(unittest.TestCase):
    def test_serialize_dataframe_empty(self):
        df = pd.DataFrame()
        result = ResponseSerializer.serialize_dataframe(df)
        self.assertEqual(result, {"columns": [], "data": [], "index": []})

    def test_serialize_dataframe_non_empty(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        result = ResponseSerializer.serialize_dataframe(df)
        expected = {"columns": ["A", "B"], "data": [[1, 3], [2, 4]], "index": [0, 1]}
        self.assertEqual(result, expected)

    @patch("builtins.open", new_callable=mock_open, read_data=b"image_data")
    @patch("base64.b64encode", return_value=b"encoded_image")
    def test_serialize_plot(self, mock_b64encode, mock_open_file):
        result = {"type": "plot", "value": "path/to/image.png"}
        serialized = ResponseSerializer.serialize(result)
        expected = {"type": "plot", "value": "encoded_image"}
        self.assertEqual(json.loads(serialized), expected)
        mock_open_file.assert_called_once_with("path/to/image.png", "rb")
        mock_b64encode.assert_called_once_with(b"image_data")

    def test_serialize_dataframe_type(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        result = {"type": "dataframe", "value": df}
        serialized = ResponseSerializer.serialize(result)
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized["type"], "dataframe")
        self.assertEqual(
            deserialized["value"], ResponseSerializer.serialize_dataframe(df)
        )

    def test_deserialize_dataframe(self):
        response = {
            "type": "dataframe",
            "value": {"columns": ["A", "B"], "data": [[1, 3], [2, 4]], "index": [0, 1]},
        }
        serialized = json.dumps(response)
        result = ResponseSerializer.deserialize(serialized)
        expected_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        pd.testing.assert_frame_equal(result["value"], expected_df)

    @patch("builtins.open", new_callable=mock_open)
    @patch("base64.b64decode", return_value=b"image_data")
    def test_deserialize_plot(self, mock_b64decode, mock_open_file):
        response = {"type": "plot", "value": base64.b64encode(b"image_data").decode()}
        serialized = json.dumps(response)
        chart_path = "path/to/output.png"
        result = ResponseSerializer.deserialize(serialized, chart_path=chart_path)
        self.assertEqual(result["value"], chart_path)
        mock_b64decode.assert_called_once_with(response["value"])
        mock_open_file.assert_called_once_with(chart_path, "wb")
        mock_open_file().write.assert_called_once_with(b"image_data")


class TestCustomEncoder(unittest.TestCase):
    def test_encode_numpy(self):
        data = {"int": np.int64(42), "float": np.float64(3.14)}
        encoded = json.dumps(data, cls=CustomEncoder)
        self.assertEqual(json.loads(encoded), {"int": 42, "float": 3.14})

    def test_encode_datetime(self):
        now = datetime.datetime.now()
        data = {"timestamp": now}
        encoded = json.dumps(data, cls=CustomEncoder)
        self.assertEqual(json.loads(encoded), {"timestamp": now.isoformat()})

    def test_encode_dataframe(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        data = {"df": df}
        encoded = json.dumps(data, cls=CustomEncoder)
        self.assertEqual(
            json.loads(encoded)["df"], ResponseSerializer.serialize_dataframe(df)
        )


if __name__ == "__main__":
    unittest.main()
