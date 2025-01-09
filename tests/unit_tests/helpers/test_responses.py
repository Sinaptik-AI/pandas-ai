import unittest

import pandas as pd

from pandasai.core.response.parser import ResponseParser
from pandasai.core.response import (
    ChartResponse,
    DataFrameResponse,
    NumberResponse,
    StringResponse,
)
from pandasai.exceptions import InvalidOutputValueMismatch


class TestResponseParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response_parser = ResponseParser()

    def test_parse_valid_number(self):
        result = {"type": "number", "value": 42}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, NumberResponse)
        self.assertEqual(response.value, 42)
        self.assertEqual(response.last_code_executed, None)
        self.assertEqual(response.type, "number")

    def test_parse_valid_string(self):
        result = {"type": "string", "value": "test string"}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, StringResponse)
        self.assertEqual(response.value, "test string")
        self.assertEqual(response.last_code_executed, None)
        self.assertEqual(response.type, "string")

    def test_parse_valid_dataframe(self):
        expected_df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        result = {"type": "dataframe", "value": expected_df}

        response = self.response_parser.parse(result)
        self.assertIsInstance(response, DataFrameResponse)
        pd.testing.assert_frame_equal(response.value, expected_df)
        self.assertEqual(response.last_code_executed, None)
        self.assertEqual(response.type, "dataframe")

    def test_parse_valid_plot(self):
        result = {"type": "plot", "value": "path/to/plot.png"}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, ChartResponse)
        self.assertEqual(response.value, "path/to/plot.png")
        self.assertEqual(response.last_code_executed, None)
        self.assertEqual(response.type, "chart")

    def test_plot_img_show_triggered(self):
        result = {
            "type": "plot",
            "value": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
        }
        response = self.response_parser.parse(result)

        mock_image = unittest.mock.MagicMock()
        with unittest.mock.patch(
            "PIL.Image.open", return_value=mock_image
        ) as mock_open:
            response.show()
            mock_open.assert_called_once()
            mock_image.show.assert_called_once()

        mock_image = unittest.mock.MagicMock()
        with unittest.mock.patch(
            "PIL.Image.open", return_value=mock_image
        ) as mock_open:
            print(response)
            mock_open.assert_called_once()
            mock_image.show.assert_called_once()

    def test_parse_with_last_code_executed(self):
        result = {"type": "number", "value": 42}
        last_code = "print('Hello, World!')"
        response = self.response_parser.parse(result, last_code)
        self.assertIsInstance(response, NumberResponse)
        self.assertEqual(response.value, 42)
        self.assertEqual(response.last_code_executed, last_code)
        self.assertEqual(response.type, "number")

    def test_parse_invalid_type(self):
        result = {"type": "unknown", "value": "test"}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser.parse(result)

    def test_parse_missing_type(self):
        result = {"value": "test"}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser.parse(result)

    def test_parse_missing_value(self):
        result = {"type": "string"}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser.parse(result)

    def test_validate_invalid_number_type(self):
        result = {"type": "number", "value": "not a number"}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser._validate_response(result)

    def test_validate_invalid_string_type(self):
        result = {"type": "string", "value": 123}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser._validate_response(result)

    def test_validate_invalid_dataframe_type(self):
        result = {"type": "dataframe", "value": "not a dataframe"}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser._validate_response(result)

    def test_validate_invalid_plot_type(self):
        result = {"type": "plot", "value": 12345}
        with self.assertRaises(InvalidOutputValueMismatch):
            self.response_parser._validate_response(result)

    def test_validate_plot_with_base64(self):
        result = {"type": "plot", "value": "data:image/png;base64 fake_image_data"}
        self.assertTrue(self.response_parser._validate_response(result))

    def test_validate_valid_plot_path(self):
        result = {"type": "plot", "value": "/valid/path/to/plot.png"}
        self.assertTrue(self.response_parser._validate_response(result))


if __name__ == "__main__":
    unittest.main()
