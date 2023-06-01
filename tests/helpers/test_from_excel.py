"""Unit tests for the from_excel function"""
import pandas as pd
import pytest

from pandasai.helpers.from_excel import from_excel


class TestFromExcel:
    """Unit tests for the from_excel function"""

    @pytest.fixture
    def mock_df(self):
        return pd.DataFrame({"A": [1, 2, 3]})

    # patch pandas.read_excel
    def mock_read_excel(*args, **kwargs):
        return pd.DataFrame({"A": [1, 2, 3]})

    def test_active_sheet(self, mock_df, monkeypatch):
        monkeypatch.setattr(pd, "read_excel", self.mock_read_excel)
        df = from_excel("../data/from_excel_data.xlsx")
        assert df.values.tolist() == mock_df.values.tolist()

    def test_sheet_name(self, mock_df, monkeypatch):
        monkeypatch.setattr(pd, "read_excel", self.mock_read_excel)
        df = from_excel("../data/from_excel_data.xlsx", sheet="Sheet1")
        assert df.values.tolist() == mock_df.values.tolist()
