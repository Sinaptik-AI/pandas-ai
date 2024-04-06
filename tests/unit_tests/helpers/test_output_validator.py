import unittest

import pandas as pd

from pandasai.helpers.output_validator import OutputValidator


class TestValidateResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output_validator = OutputValidator()

    def test_valid_number_result(self):
        result = {"type": "number", "value": 42}
        self.assertTrue(self.output_validator.validate_result(result))

    def test_invalid_number_result(self):
        result = {"type": "number", "value": "invalid"}
        self.assertFalse(self.output_validator.validate_result(result))

    def test_valid_string_result(self):
        result = {"type": "string", "value": "test"}
        self.assertTrue(self.output_validator.validate_result(result))

    def test_invalid_string_result(self):
        result = {"type": "string", "value": 42}
        self.assertFalse(self.output_validator.validate_result(result))

    def test_valid_dataframe_result(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        result = {"type": "dataframe", "value": df}
        self.assertTrue(self.output_validator.validate_result(result))

    def test_invalid_dataframe_result(self):
        result = {"type": "dataframe", "value": "invalid"}
        self.assertFalse(self.output_validator.validate_result(result))

    def test_valid_plot_result(self):
        result = {"type": "plot", "value": "/path/to/plot.png"}
        self.assertTrue(self.output_validator.validate_result(result))

    def test_valid_plot_dict_result(self):
        result = {"type": "plot", "value": {"data": [1, 2, 3]}}
        self.assertTrue(self.output_validator.validate_result(result))

    def test_invalid_plot_result(self):
        result = {"type": "plot", "value": 42}
        self.assertFalse(self.output_validator.validate_result(result))
