import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from pandasai.dataset_loader import DatasetLoader
from pandasai.dataframe.base import DataFrame


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
            ],
            "order_by": ["created_at DESC"],
            "limit": 100,
            "transformations": [{"type": "anonymize", "params": {"column": "email"}}],
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
            "pandasai.dataset_loader.DatasetLoader._read_cache"
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

    def test_load_from_database(self, sample_schema):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getmtime", return_value=pd.Timestamp.now().timestamp() - 86400 * 8
        ), patch(
            "pandasai.dataset_loader.DatasetLoader._load_from_mysql"
        ) as mock_load_from_mysql, patch(
            "pandasai.dataset_loader.DatasetLoader._cache_data"
        ) as mock_cache_data, patch(
            "builtins.open", mock_open(read_data=str(sample_schema))
        ):
            loader = DatasetLoader()
            mock_load_from_mysql.return_value = pd.DataFrame(
                {"email": ["test@example.com"]}
            )

            result = loader.load("test/users")

            assert isinstance(result, DataFrame)
            assert "email" in result.columns
            mock_load_from_mysql.assert_called_once()
            mock_cache_data.assert_called_once()

    def test_generate_query(self, sample_schema):
        loader = DatasetLoader()
        query = loader._generate_query(sample_schema)
        expected_query = (
            "SELECT email, first_name FROM users ORDER BY created_at DESC LIMIT 100"
        )
        assert query == expected_query

    def test_anonymize(self):
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
