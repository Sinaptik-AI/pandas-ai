import unittest
from pandasai.exceptions import InvalidOutputValueMismatch
from pandasai.core.response.base import ResponseParser
from pandasai.core.response.response_types import Chart, DataFrame, Number, String
import pandas as pd


class TestResponseParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response_parser = ResponseParser()

    def test_parse_valid_number(self):
        result = {"type": "number", "value": 42}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, Number)

    def test_parse_valid_string(self):
        result = {"type": "string", "value": "test string"}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, String)

    def test_parse_valid_dataframe(self):
        result = {
            "type": "dataframe",
            "value": pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]}),
        }

        response = self.response_parser.parse(result)
        self.assertIsInstance(response, DataFrame)

    def test_parse_valid_plot(self):
        result = {"type": "plot", "value": "path/to/plot.png"}
        response = self.response_parser.parse(result)
        self.assertIsInstance(response, Chart)

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
