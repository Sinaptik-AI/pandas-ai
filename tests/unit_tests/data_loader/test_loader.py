from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from pandasai.data_loader.loader import DatasetLoader
from pandasai.data_loader.local_loader import LocalDatasetLoader
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import InvalidDataSourceType


class TestDatasetLoader:
    def test_load_from_local_source_valid(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "pandasai.data_loader.local_loader.LocalDatasetLoader._read_csv_or_parquet"
        ) as mock_read_csv_or_parquet:
            loader = LocalDatasetLoader(sample_schema, "test")

            mock_read_csv_or_parquet.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )

            result = loader._load_from_local_source()

            assert isinstance(result, DataFrame)
            mock_read_csv_or_parquet.assert_called_once()
            assert "email" in result.columns

    def test_load_from_local_source_invalid_source_type(self, sample_schema):
        sample_schema.source.type = "mysql"
        loader = LocalDatasetLoader(sample_schema, "test")

        with pytest.raises(
            InvalidDataSourceType, match="Unsupported local source type"
        ):
            loader._load_from_local_source()

    def test_load_schema(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(sample_schema.to_yaml()))
        ):
            schema = DatasetLoader._read_schema_file("test/users")
            assert schema == sample_schema

    def test_load_schema_mysql(self, mysql_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ):
            schema = DatasetLoader._read_schema_file("test/users")
            assert schema == mysql_schema

    def test_load_schema_mysql_sanitized_name(self, mysql_schema):
        mysql_schema.name = "non-sanitized-name"

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ):
            schema = DatasetLoader._read_schema_file("test/users")
            assert schema.name == "non_sanitized_name"

    def test_load_schema_file_not_found(self):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                DatasetLoader._read_schema_file("test/users")

    def test_read_parquet(self, sample_schema):
        loader = LocalDatasetLoader(sample_schema, "test")

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_parquet", return_value=mock_df) as mock_read_parquet:
            result = loader._read_csv_or_parquet("dummy_path", "parquet")
            mock_read_parquet.assert_called_once()
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_csv(self, sample_schema):
        loader = LocalDatasetLoader(sample_schema, "test")

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
            result = loader._read_csv_or_parquet("dummy_path", "csv")
            mock_read_csv.assert_called_once()
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_csv_or_parquet_unsupported_format(self, sample_schema):
        loader = LocalDatasetLoader(sample_schema, "test")

        with pytest.raises(ValueError, match="Unsupported file format: unsupported"):
            loader._read_csv_or_parquet("dummy_path", "unsupported")

    def test_apply_transformations(self, sample_schema):
        """Test that DatasetLoader correctly uses TransformationManager."""
        loader = LocalDatasetLoader(sample_schema, "test")

        df = pd.DataFrame(
            {
                "email": ["user1@example.com"],
                "timestamp": pd.to_datetime(["2023-01-01T00:00:00+00:00"]),
            }
        )

        result = loader._apply_transformations(df)

        # We just need to verify that transformations were applied
        # Detailed transformation tests are in test_transformation_manager.py
        assert "@example.com" in result.iloc[0]["email"]
        assert result.iloc[0]["email"] != "user1@example.com"
        assert result.iloc[0]["timestamp"].tzname() == "UTC"

    def test_build_dataset_csv_schema(self, sample_schema):
        """Test loading data from a CSV schema directly and creates a VirtualDataFrame and handles queries correctly."""
        with patch("os.path.exists", return_value=True), patch(
            "pandasai.data_loader.local_loader.LocalDatasetLoader._read_csv_or_parquet"
        ) as mock_read_csv_or_parquet, patch(
            "pandasai.data_loader.local_loader.LocalDatasetLoader._apply_transformations"
        ) as mock_apply_transformations:
            mock_read_csv_or_parquet.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )
            mock_apply_transformations.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )
            loader = LocalDatasetLoader(sample_schema, "test/test")

            result = loader.load()

            assert isinstance(result, DataFrame)
            assert "email" in result.columns

    def test_filter_columns_with_schema_columns(self, sample_schema):
        """Test that columns are filtered correctly when schema columns are specified."""
        loader = LocalDatasetLoader(sample_schema, "test/test")

        # Create a DataFrame with extra columns
        df = pd.DataFrame(
            {
                "email": ["test@example.com"],
                "first_name": ["John"],
                "timestamp": ["2023-01-01"],
                "extra_col": ["extra"],  # This column should be filtered out
            }
        )

        filtered_df = loader._filter_columns(df)
        assert list(filtered_df.columns) == ["email", "first_name", "timestamp"]
        assert "extra_col" not in filtered_df.columns

    def test_filter_columns_without_schema_columns(self):
        """Test that all columns are kept when no schema columns are specified."""
        loader = LocalDatasetLoader(
            SemanticLayerSchema(
                **{
                    "name": "Users",
                    "source": {"type": "csv", "path": "users.csv", "table": "table"},
                }
            ),
            "test/test",
        )

        df = pd.DataFrame({"col1": [1], "col2": [2], "col3": [3]})

        filtered_df = loader._filter_columns(df)
        assert list(filtered_df.columns) == ["col1", "col2", "col3"]

    def test_filter_columns_with_non_matching_columns(self, sample_schema):
        """Test filtering when schema columns don't match DataFrame columns."""
        loader = LocalDatasetLoader(sample_schema, "test/test")

        # Create DataFrame with none of the schema columns
        df = pd.DataFrame({"different_col1": [1], "different_col2": [2]})

        filtered_df = loader._filter_columns(df)
        assert len(filtered_df.columns) == 0  # Should return empty DataFrame
