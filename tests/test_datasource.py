import pandas as pd
import pytest

from pandasai.helpers.datasource import *


class TestDataSource:
    def sheets_input_valid(self):
        assert (
            sheets_input("1IRGJFUpCR0-9tPDk2MgPjQCtNft_4a8B1fHgYK7_LM8", "second")
            is pd.DataFrame
        )

    def sheets_input_not_none(self):
        assert (
            sheets_input("1IRGJFUpCR0-9tPDk2MgPjQCtNft_4a8B1fHgYK7_LM8", "second")
            is not None
        )
