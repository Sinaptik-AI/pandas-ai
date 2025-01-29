import logging
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

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
        }
        return SemanticLayerSchema(**raw_schema)

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
            schema = loader._read_local_schema()
            assert schema == sample_schema

    def test_load_schema_mysql(self, mysql_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            schema = loader._read_local_schema()
            assert schema == mysql_schema

    def test_load_schema_mysql_sanitized_name(self, mysql_schema):
        mysql_schema.name = "non-sanitized-name"

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(mysql_schema.to_yaml()))
        ):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            schema = loader._read_local_schema()
            assert schema.name == "non_sanitized_name"

    def test_load_schema_file_not_found(self):
        with patch("os.path.exists", return_value=False):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            with pytest.raises(FileNotFoundError):
                loader._read_local_schema()

    def test_read_parquet(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_parquet", return_value=mock_df) as mock_read_parquet:
            result = loader._read_csv_or_parquet("dummy_path", "parquet")
            mock_read_parquet.assert_called_once()
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_csv(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_csv", return_value=mock_df) as mock_read_csv:
            result = loader._read_csv_or_parquet("dummy_path", "csv")
            mock_read_csv.assert_called_once()
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_csv_or_parquet_unsupported_format(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        with pytest.raises(ValueError, match="Unsupported file format: unsupported"):
            loader._read_csv_or_parquet("dummy_path", "unsupported")

    def test_apply_transformations(self, sample_schema):
        """Test that DatasetLoader correctly uses TransformationManager."""
        loader = DatasetLoader()
        loader.schema = sample_schema

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

    def test_build_dataset_mysql_schema(self, mysql_schema):
        """Test loading data from a MySQL schema directly and creates a VirtualDataFrame and handles queries correctly."""
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
            result = loader._build_dataset(
                schema=mysql_schema, dataset_path="test/test"
            )

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

    def test_build_dataset_csv_schema(self, sample_schema):
        """Test loading data from a CSV schema directly and creates a VirtualDataFrame and handles queries correctly."""
        with patch("os.path.exists", return_value=True), patch(
            "pandasai.data_loader.loader.DatasetLoader._read_csv_or_parquet"
        ) as mock_read_csv_or_parquet, patch(
            "pandasai.data_loader.loader.DatasetLoader._apply_transformations"
        ) as mock_apply_transformations:
            mock_read_csv_or_parquet.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )
            mock_apply_transformations.return_value = DataFrame(
                {"email": ["test@example.com"]}
            )
            loader = DatasetLoader()

            result = loader._build_dataset(
                schema=sample_schema, dataset_path="test/test"
            )

            assert isinstance(result, DataFrame)
            assert "email" in result.columns
