"""
Unit tests for the FileImporter class
"""

import pandas as pd
import pytest

from pandasai.helpers.file_importer import FileImporter


class TestFileImporter:
    """
    Unit tests for the SmartDataframe class
    """

    @pytest.fixture
    def mocked_df(self):
        return pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})

    def test_import_csv_file(self, mocked_df, mocker):
        mocker.patch.object(
            pd,
            "read_csv",
            return_value=mocked_df,
        )
        df = FileImporter.import_from_file("sample.csv")
        assert isinstance(df, pd.DataFrame)
        assert df.equals(mocked_df)

    def test_import_parquet_file(self, mocked_df, mocker):
        mocker.patch.object(pd, "read_parquet", return_value=mocked_df)
        df = FileImporter.import_from_file("sample.parquet")
        assert isinstance(df, pd.DataFrame)
        assert df.equals(mocked_df)

    def test_import_excel_file(self, mocked_df, mocker):
        mocker.patch.object(
            pd,
            "read_excel",
            return_value=mocked_df,
        )
        df = FileImporter.import_from_file("sample.xlsx")
        assert isinstance(df, pd.DataFrame)
        assert df.equals(mocked_df)

    @pytest.mark.parametrize("file_path", ["sample.txt", "sample.docx", "sample.pdf"])
    def test_invalid_file_format(self, file_path):
        with pytest.raises(ValueError):
            FileImporter.import_from_file(file_path)
