import logging
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pandasai import VirtualDataFrame
from pandasai.data_loader.sql_loader import SQLDatasetLoader
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError


class TestSqlDatasetLoader:
    def test_load_mysql_source(self, mysql_schema):
        """Test loading data from a MySQL source creates a VirtualDataFrame and handles queries correctly."""
        with patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader.execute_query"
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

            loader = SQLDatasetLoader(mysql_schema, "test/users")
            result = loader.load()

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

    def test_mysql_schema(self, mysql_schema):
        """Test loading data from a MySQL schema directly and creates a VirtualDataFrame and handles queries correctly."""
        with patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader.execute_query"
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

            loader = SQLDatasetLoader(mysql_schema, "test/test")
            logging.debug("Loading schema from dataset path: %s", loader)
            result = loader.load()

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

    def test_load_with_transformation(self, mysql_schema):
        """Test loading data from a MySQL source creates a VirtualDataFrame and handles queries correctly."""
        with patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function"
        ) as mock_get_loader_function:
            # Mock the query results

            dti = pd.to_datetime(["2025-01-31 10:29:12.694309"])
            dti = dti.tz_localize("Europe/Berlin")

            loader_function = MagicMock()
            loader_function.return_value = pd.DataFrame(
                {
                    "email": ["test@example.com"],
                    "first_name": ["John"],
                    "timestamp": dti,
                }
            )

            mock_get_loader_function.return_value = loader_function

            loader = SQLDatasetLoader(mysql_schema, "test/users")
            result = loader.load()

            # Test that we get a VirtualDataFrame
            assert isinstance(result, VirtualDataFrame)
            assert result.schema == mysql_schema

            # Test that load_head() works
            head_result = result.head()
            assert isinstance(head_result, pd.DataFrame)
            assert "email" in head_result.columns
            assert head_result["email"][0] == "****@example.com"
            assert head_result["timestamp"][0] == dti[0].tz_convert("UTC")
            assert "first_name" in head_result.columns
            assert "timestamp" in head_result.columns

            # Verify the SQL query was executed correctly
            loader_function.assert_called_once()
            assert (
                loader_function.call_args[0][1]
                == "SELECT email, first_name, timestamp FROM users ORDER BY RAND() LIMIT 5"
            )

    def test_mysql_malicious_query(self, mysql_schema):
        """Test loading data from a MySQL source creates a VirtualDataFrame and handles queries correctly."""
        with patch(
            "pandasai.data_loader.sql_loader.is_sql_query_safe"
        ) as mock_sql_query, patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function"
        ) as mock_loader_function:
            mocked_exec_function = MagicMock()
            mock_df = DataFrame(
                pd.DataFrame(
                    {
                        "email": ["test@example.com"],
                        "first_name": ["John"],
                        "timestamp": [pd.Timestamp.now()],
                    }
                )
            )
            mocked_exec_function.return_value = mock_df
            mock_loader_function.return_value = mocked_exec_function
            loader = SQLDatasetLoader(mysql_schema, "test/users")
            mock_sql_query.return_value = False
            logging.debug("Loading schema from dataset path: %s", loader)

            with pytest.raises(MaliciousQueryError):
                loader.execute_query("DROP TABLE users")

            mock_sql_query.assert_called_once_with("DROP TABLE users")

    def test_mysql_safe_query(self, mysql_schema):
        """Test loading data from a MySQL source creates a VirtualDataFrame and handles queries correctly."""
        with patch(
            "pandasai.data_loader.sql_loader.is_sql_query_safe"
        ) as mock_sql_query, patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function"
        ) as mock_loader_function, patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader._apply_transformations"
        ) as mock_apply_transformations:
            mocked_exec_function = MagicMock()
            mock_df = DataFrame(
                pd.DataFrame(
                    {
                        "email": ["test@example.com"],
                        "first_name": ["John"],
                        "timestamp": [pd.Timestamp.now()],
                    }
                )
            )
            mocked_exec_function.return_value = mock_df
            mock_apply_transformations.return_value = mock_df
            mock_loader_function.return_value = mocked_exec_function
            loader = SQLDatasetLoader(mysql_schema, "test/users")
            mock_sql_query.return_value = True
            logging.debug("Loading schema from dataset path: %s", loader)

            result = loader.execute_query("select * from users")

            assert isinstance(result, DataFrame)
            mock_sql_query.assert_called_once_with("select * from users")
