import logging
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from pandasai import VirtualDataFrame
from pandasai.data_loader.sql_loader import SQLDatasetLoader
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError
from pandasai.exceptions import InvalidDataSourceType

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
                """SELECT
  email,
  first_name,
  timestamp
FROM users
LIMIT 5"""
            )
            # Test executing a custom query
            custom_query = "SELECT email FROM users WHERE first_name = 'John'"
            result.execute_sql_query(custom_query)
            mock_execute_query.assert_called_with(custom_query)

    def test_load_with_transformation(self, mysql_schema):
        """Test loading data with transformation creates a VirtualDataFrame and handles queries correctly."""
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
            # Test that we get a VirtualDataFrame with transformation applied
            assert isinstance(result, VirtualDataFrame)
            assert result.schema == mysql_schema
            head_result = result.head()
            assert isinstance(head_result, pd.DataFrame)
            assert "email" in head_result.columns
            assert head_result["email"][0] == "****@example.com"
            assert head_result["timestamp"][0] == dti[0].tz_convert("UTC")
            assert "first_name" in head_result.columns
            assert "timestamp" in head_result.columns
            loader_function.assert_called_once()

    def test_mysql_malicious_query(self, mysql_schema):
        """Test that a malicious SQL query is detected and raises an error."""
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
        """Test that a safe SQL query executes correctly."""
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
            result = loader.execute_query("SELECT * FROM users")
            assert isinstance(result, DataFrame)
            mock_sql_query.assert_called_once_with("SELECT\n  *\nFROM users")

    def test_mysql_malicious_with_no_import(self, mysql_schema):
        """Test that a ModuleNotFoundError during query execution is converted to ImportError."""
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
            mock_exec_function = MagicMock()
            mock_loader_function.return_value = mock_exec_function
            mock_exec_function.side_effect = ModuleNotFoundError("Error")
            loader = SQLDatasetLoader(mysql_schema, "test/users")
            mock_sql_query.return_value = True
            logging.debug("Loading schema from dataset path: %s", loader)
            with pytest.raises(ImportError):
                loader.execute_query("select * from users")

    def test_execute_query_runtime_error(self, mysql_schema):
        """
        Test that execute_query raises a RuntimeError when an unexpected exception occurs during query execution.
        """
        with patch("pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function") as mock_get_loader_function, \
             patch("pandasai.data_loader.sql_loader.is_sql_query_safe") as mock_is_safe, \
             patch("pandasai.data_loader.sql_loader.SQLParser.transpile_sql_dialect", return_value="SELECT * FROM users"):
            mock_is_safe.return_value = True
            def failing_loader(connection_info, query, params):
                raise Exception("Generic failure")
            mock_get_loader_function.return_value = failing_loader
            loader = SQLDatasetLoader(mysql_schema, "test/users")
            with pytest.raises(RuntimeError, match="Failed to execute query for '.*' with: SELECT \\* FROM users"):
                loader.execute_query("SELECT * FROM users")

    def test_get_row_count_success(self, mysql_schema):
        """
        Test that get_row_count retrieves the correct row count from the resulting DataFrame.
        """
        loader = SQLDatasetLoader(mysql_schema, "test/users")
        with patch.object(loader.query_builder, 'get_row_count', return_value="fake_count_query") as mock_get_count_query, \
             patch.object(loader, 'execute_query', return_value=pd.DataFrame([[123]])) as mock_execute_query:
            row_count = loader.get_row_count()
            mock_get_count_query.assert_called_once()
            mock_execute_query.assert_called_once_with("fake_count_query")
            assert row_count == 123

    def test_execute_query_with_params(self, mysql_schema):
        """
        Test that execute_query forwards parameters to the loader function, applies SQL transpilation,
        verifies query safety, and applies any transformations on the resulting DataFrame.
        """
        with patch("pandasai.data_loader.sql_loader.SQLParser.transpile_sql_dialect", return_value="transformed query") as mock_transpile, \
             patch("pandasai.data_loader.sql_loader.is_sql_query_safe", return_value=True) as mock_safe, \
             patch("pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function") as mock_get_loader, \
             patch.object(SQLDatasetLoader, "_apply_transformations", return_value=pd.DataFrame({"col": [1]})) as mock_transform:
            fake_df = pd.DataFrame({"col": [42]})
            fake_loader = MagicMock(return_value=fake_df)
            mock_get_loader.return_value = fake_loader
            loader = SQLDatasetLoader(mysql_schema, "test/table")
            result = loader.execute_query("SELECT * FROM table", params=["param1", "param2"])
            mock_transpile.assert_called_once_with("SELECT * FROM table", to_dialect=mysql_schema.source.type)
            mock_safe.assert_called_once_with("transformed query")
            fake_connection_info = mysql_schema.source.connection
            fake_loader.assert_called_once_with(fake_connection_info, "transformed query", ["param1", "param2"])
            mock_transform.assert_called_once_with(fake_df)
            pd.testing.assert_frame_equal(result, pd.DataFrame({"col": [1]}))

    def test_execute_query_no_params(self, mysql_schema):
        """
        Test that execute_query correctly forwards params as None when no parameters argument is provided.
        Verifies that:
          - SQLParser.transpile_sql_dialect is called with the original query and correct dialect.
          - is_sql_query_safe is called on the transformed query.
          - The loader function is invoked with connection info, the transformed query and params=None.
          - The result is correctly passed through _apply_transformations.
        """
        with patch(
            "pandasai.data_loader.sql_loader.SQLParser.transpile_sql_dialect",
            return_value="transformed query"
        ) as mock_transpile, \
        patch(
            "pandasai.data_loader.sql_loader.is_sql_query_safe",
            return_value=True
        ) as mock_safe, \
        patch(
            "pandasai.data_loader.sql_loader.SQLDatasetLoader._get_loader_function"
        ) as mock_get_loader, \
        patch.object(
            SQLDatasetLoader, "_apply_transformations",
            return_value=pd.DataFrame({"no_params": [1]})
        ) as mock_transform:
            fake_df = pd.DataFrame({"dummy": [100]})
            fake_loader = MagicMock(return_value=fake_df)
            mock_get_loader.return_value = fake_loader
            loader = SQLDatasetLoader(mysql_schema, "test/table")
            result = loader.execute_query("SELECT * FROM table")
            mock_transpile.assert_called_once_with(
                "SELECT * FROM table",
                to_dialect=mysql_schema.source.type
            )
            mock_safe.assert_called_once_with("transformed query")
            fake_connection_info = mysql_schema.source.connection
            fake_loader.assert_called_once_with(fake_connection_info, "transformed query", None)
            pd.testing.assert_frame_equal(result, pd.DataFrame({"no_params": [1]}))

def test_invalid_source_type():
    """
    Test that _get_loader_function raises an InvalidDataSourceType error when given an unsupported data source type.
    """
    with pytest.raises(InvalidDataSourceType):
        SQLDatasetLoader._get_loader_function("unsupported")
