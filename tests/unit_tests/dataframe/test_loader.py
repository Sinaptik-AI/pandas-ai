import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.loader import DatasetLoader
from datetime import datetime, timedelta


class TestDatasetLoader:
    @pytest.fixture
    def sample_schema(self):
        return {
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

    def test_load_from_cache(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getmtime", return_value=pd.Timestamp.now().timestamp()
        ), patch(
            "pandasai.dataframe.loader.DatasetLoader._read_cache"
        ) as mock_read_cache, patch(
            "builtins.open", mock_open(read_data=str(sample_schema))
        ):
            loader = DatasetLoader()
            mock_read_cache.return_value = DataFrame(
                pd.DataFrame({"email": ["test@example.com"]})
            )

            result = loader.load("test/users")

            assert isinstance(result, DataFrame)
            assert "email" in result.columns
            mock_read_cache.assert_called_once()

    def test_anonymize_method(self):
        loader = DatasetLoader()
        email = "test@example.com"
        anonymized = loader._anonymize(email)
        assert anonymized != email
        assert "@example.com" in anonymized

    def test_unsupported_database_type(self, sample_schema):
        unsupported_schema = sample_schema.copy()
        unsupported_schema["source"]["type"] = "unsupported_db"

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(unsupported_schema))
        ):
            loader = DatasetLoader()
            with pytest.raises(
                ValueError, match="Unsupported database type: unsupported_db"
            ):
                loader.load("test/users")

    def test_load_schema(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=str(sample_schema))
        ):
            loader = DatasetLoader()
            loader.dataset_path = "test/users"
            loader._load_schema()
            assert loader.schema == sample_schema

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
        assert cache_path == "datasets/test/users/users.parquet"

    def test_get_cache_file_path_without_destination_path(self, sample_schema):
        schema_without_path = sample_schema.copy()
        del schema_without_path["destination"]["path"]
        loader = DatasetLoader()
        loader.schema = schema_without_path
        loader.dataset_path = "test/users"
        cache_path = loader._get_cache_file_path()
        assert cache_path == "datasets/test/users/data.parquet"

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
            result = loader._read_cache("dummy_path")
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_cache_csv(self, sample_schema):
        schema_csv = sample_schema.copy()
        schema_csv["destination"]["format"] = "csv"
        loader = DatasetLoader()
        loader.schema = schema_csv

        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        with patch("pandas.read_csv", return_value=mock_df):
            result = loader._read_cache("dummy_path")
            assert isinstance(result, pd.DataFrame)
            assert result.equals(mock_df)

    def test_read_cache_unsupported_format(self, sample_schema):
        schema_unsupported = sample_schema.copy()
        schema_unsupported["destination"]["format"] = "unsupported"
        loader = DatasetLoader()
        loader.schema = schema_unsupported

        with pytest.raises(ValueError, match="Unsupported cache format: unsupported"):
            loader._read_cache("dummy_path")

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
        assert all(ts.tzinfo.zone == "UTC" for ts in result["timestamp"])

    def test_cache_data(self, sample_schema):
        loader = DatasetLoader()
        loader.schema = sample_schema

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with patch("pandas.DataFrame.to_parquet") as mock_to_parquet:
            loader._cache_data(df, "dummy_path")
            mock_to_parquet.assert_called_once_with("dummy_path", index=False)

        schema_csv = sample_schema.copy()
        schema_csv["destination"]["format"] = "csv"
        loader.schema = schema_csv

        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            loader._cache_data(df, "dummy_path")
            mock_to_csv.assert_called_once_with("dummy_path", index=False)

        schema_unsupported = sample_schema.copy()
        schema_unsupported["destination"]["format"] = "unsupported"
        loader.schema = schema_unsupported

        with pytest.raises(ValueError, match="Unsupported cache format: unsupported"):
            loader._cache_data(df, "dummy_path")


# Add more tests for _load_from_source and other methods as needed
