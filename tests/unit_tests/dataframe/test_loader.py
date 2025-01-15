import logging
import sys
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
import yaml

from pandasai.data_loader.loader import DatasetLoader
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import InvalidDataSourceType


class TestDatasetLoader:
    @pytest.fixture
    def sample_schema(self):
        raw_schema = {
            "name": "Users",
            "update_frequency": "weekly",
            "columns": [
                {
                    "name": "email",
                    "type": "string",
                    "description": "User's email address",
                },
                {
                    "name": "first_name",
                    "type": "string",
                    "description": "User's first name",
                },
                {
                    "name": "timestamp",
                    "type": "datetime",
                    "description": "Timestamp of the record",
                },
            ],
            "order_by": ["created_at DESC"],
            "limit": 100,
            "transformations": [
                {"type": "anonymize", "params": {"column": "email"}},
                {
                    "type": "convert_timezone",
                    "params": {"column": "timestamp", "to": "UTC"},
                },
            ],
            "source": {
                "type": "csv",
                "path": "users.csv",
            },
            "destination": {
                "type": "local",
                "format": "parquet",
                "path": "users.parquet",
            },
        }
        return SemanticLayerSchema(**raw_schema)

    @pytest.fixture
    def mysql_schema(self):
        raw_schema = {
            "name": "Users",
            "update_frequency": "weekly",
            "columns": [
                {
                    "name": "email",
                    "type": "string",
                    "description": "User's email address",
                },
                {
                    "name": "first_name",
                    "type": "string",
                    "description": "User's first name",
                },
                {
                    "name": "timestamp",
                    "type": "datetime",
                    "description": "Timestamp of the record",
                },
            ],
            "order_by": ["created_at DESC"],
            "limit": 100,
            "transformations": [
                {"type": "anonymize", "params": {"column": "email"}},
                {
                    "type": "convert_timezone",
                    "params": {"column": "timestamp", "to": "UTC"},
                },
            ],
            "source": {
                "type": "mysql",
                "connection": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "test_db",
                    "user": "test_user",
                    "password": "test_password",
                },
                "table": "users",
            },
            "destination": {
                "type": "local",
                "format": "parquet",
                "path": "users.parquet",
            },
        }
        return SemanticLayerSchema(**raw_schema)

    def test_load_from_cache(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getmtime", return_value=pd.Timestamp.now().timestamp()
        ), patch(
            "pandasai.data_loader.loader.DatasetLoader._read_csv_or_parquet"
        ) as mock_read_cache, patch(
            "builtins.open", mock_open(read_data=str(sample_schema.to_yaml()))
        ), patch(
            "pandasai.data_loader.loader.DatasetLoader._load_from_local_source"
        ) as mock_load_local_source, patch(
            "pandasai.data_loader.loader.DatasetLoader.load_head"
        ) as mock_load_head:
            loader = DatasetLoader()
            mock_read_cache.return_value = DataFrame(
                pd.DataFrame({"email": ["test@example.com"]})
            )
            mock_load_head.return_value = DataFrame(
                pd.DataFrame({"email": ["test@example.com"]})
            )

            result = loader.load("test/users")

            assert isinstance(result, DataFrame)
            assert "email" in result.columns
            mock_read_cache.assert_called_once()
            mock_load_local_source.assert_not_called()

    def test_load_from_local_source_valid(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "pandasai.data_loader.loader.DatasetLoader._read_csv_or_parquet"
        ) as mock_read_csv_or_parquet:
            loader = DatasetLoader()
            loader.dataset_path = "test"
            loader.schema = sample_schema

            mock_read_csv_or_parquet.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )

            result = loader._load_from_local_source()

            assert isinstance(result, DataFrame)
            assert "email" in result.columns

    def test_load_from_local_source_invalid_source_type(self, sample_schema):
        loader = DatasetLoader()
        sample_schema.source.type = "mysql"
        loader.schema = sample_schema

        with pytest.raises(
            InvalidDataSourceType, match="Unsupported local source type"
        ):
            loader._load_from_local_source()

    def test_anonymize_method(self):
        loader = DatasetLoader()
        email = "test@example.com"
        anonymized = loader._anonymize(email)
        assert anonymized != email
        assert "@example.com" in anonymized

    def test_load_schema(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(sample_schema.to_yaml()))
        ):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            loader._load_schema()
            assert loader.schema == sample_schema

    def test_load_schema_mysql(self, mysql_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            loader._load_schema()
            assert loader.schema == mysql_schema

    def test_load_schema_file_not_found(self):
        with patch("os.path.exists", return_value=False):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            with pytest.raises(FileNotFoundError):
                loader._load_schema()

    def test_get_cache_file_path_with_destination_path(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema
        loader.dataset_path = "test/users"
        cache_path = loader._get_cache_file_path()
        if sys.platform.startswith("win"):
            assert cache_path.endswith("datasets\\test/users\\users.parquet")
        else:
            assert cache_path.endswith("datasets/test/users/users.parquet")

    def test_get_cache_file_path_without_destination_path(self, sample_schema):
        sample_schema.destination.path = None
        loader = DatasetLoader()
        loader.schema = sample_schema
        loader.dataset_path = "test/users"
        cache_path = loader._get_cache_file_path()
        if sys.platform.startswith("win"):
            assert cache_path.endswith("datasets\\test/users\\data.parquet")
        else:
            assert cache_path.endswith("datasets/test/users/data.parquet")

    def test_is_cache_valid(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        # Test with a recent file (should be valid)
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getmtime", return_value=datetime.now().timestamp()
        ):
            assert loader._is_cache_valid("dummy_path") is True

        # Test with an old file (should be invalid)
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getmtime",
            return_value=(datetime.now() - timedelta(weeks=2)).timestamp(),
        ):
            assert loader._is_cache_valid("dummy_path") is False

        # Test with non-existent file (should be invalid)
        with patch("os.path.exists", return_value=False):
            assert loader._is_cache_valid("dummy_path") is False

    def test_read_cache_parquet(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_parquet", return_value=mock_df):
            result = loader._read_csv_or_parquet("dummy_path", "parquet")
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_cache_csv(self, sample_schema):
        sample_schema.destination.format = "csv"
        loader = DatasetLoader()
        loader.schema = sample_schema

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_csv", return_value=mock_df):
            result = loader._read_csv_or_parquet("dummy_path", "csv")
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_cache_unsupported_format(self, sample_schema):
        sample_schema.destination.format = "unsupported"
        loader = DatasetLoader()
        loader.schema = sample_schema

        with pytest.raises(ValueError, match="Unsupported file format: unsupported"):
            loader._read_csv_or_parquet("dummy_path", "unsupported")

    def test_apply_transformations(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        df = pd.DataFrame(
            {
                "email": ["user1@example.com", "user2@example.com"],
                "timestamp": pd.to_datetime(
                    ["2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00"]
                ),
            }
        )

        result = loader._apply_transformations(df)

        # Check anonymization
        assert all(result["email"].str.contains("@example.com"))
        assert not any(result["email"].isin(["user1@example.com", "user2@example.com"]))

        # Check timezone conversion
        assert all(ts.tzinfo is not None for ts in result["timestamp"])
        assert all(ts.tzname() == "UTC" for ts in result["timestamp"])

    def test_cache_data(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
            loader._cache_data(df, "dummy_path")
            mock_to_parquet.assert_called_once_with("dummy_path", index=False)

        sample_schema.destination.format = "csv"
        loader.schema = sample_schema

        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            loader._cache_data(df, "dummy_path")
            mock_to_csv.assert_called_once_with("dummy_path", index=False)

    def test_load_mysql_source(self, mysql_schema):
        """Test loading data from a MySQL source creates a VirtualDataFrame and handles queries correctly."""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ), patch(
            "pandasai.data_loader.loader.DatasetLoader.execute_query"
        ) as mock_execute_query:
            # Mock the query results
            mock_execute_query.return_value = DataFrame(
                pd.DataFrame(
                    {
                        "email": ["test@example.com"],
                        "first_name": ["John"],
                        "timestamp": [pd.Timestamp.now()],
                    }
                )
            )

            loader = DatasetLoader()
            logging.debug("Loading schema from dataset path: %s", loader)
            result = loader.load("test/users")

            # Test that we get a VirtualDataFrame
            assert isinstance(result, DataFrame)
            assert result.schema == mysql_schema

            # Test that load_head() works
            head_result = result.head()
            assert isinstance(head_result, DataFrame)
            assert "email" in head_result.columns
            assert "first_name" in head_result.columns
            assert "timestamp" in head_result.columns

            # Verify the SQL query was executed correctly
            mock_execute_query.assert_called_once_with(
                "SELECT email, first_name, timestamp FROM users ORDER BY RAND() LIMIT 5"
            )

            # Test executing a custom query
            custom_query = "SELECT email FROM users WHERE first_name = 'John'"
            result.execute_sql_query(custom_query)
            mock_execute_query.assert_called_with(custom_query)
