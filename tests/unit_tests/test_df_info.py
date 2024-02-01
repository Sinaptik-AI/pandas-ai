import unittest

import modin.pandas as mpd
import pandas as pd
import polars as pl

from pandasai.helpers.df_info import df_type


class TestDfInfo(unittest.TestCase):
    def setUp(self):
        self.pd_df = pd.DataFrame(
            {"A": [1, 2, 3], "B": ["foo", "bar", "baz"], "C": [1.0, 2.0, 3.0]}
        )
        self.mpd_df = mpd.DataFrame(
            {"A": [1, 2, 3], "B": ["foo", "bar", "baz"], "C": [1.0, 2.0, 3.0]}
        )
        self.pl_df = None
        if "pl" in globals():
            self.pl_df = pl.DataFrame(
                {"A": [1, 2, 3], "B": ["foo", "bar", "baz"], "C": [1.0, 2.0, 3.0]}
            )

    def test_df_type_pandas(self):
        actual_output = df_type(self.pd_df)
        expected_output = "pandas"
        self.assertEqual(actual_output, expected_output)

    def test_df_type_polars(self):
        if self.pl_df is not None:
            actual_output = df_type(self.pl_df)
            expected_output = "polars"
            self.assertEqual(actual_output, expected_output)

    def test_df_type_modin(self):
        actual_output = df_type(self.mpd_df)
        expected_output = "modin"
        self.assertEqual(actual_output, expected_output)

    def test_df_type_none(self):
        actual_output = df_type("not a dataframe")
        expected_output = None
        self.assertEqual(actual_output, expected_output)
