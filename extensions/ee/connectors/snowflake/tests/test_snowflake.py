import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pandasai_snowflake import load_from_snowflake


class TestSnowflakeLoader(unittest.TestCase):
    @patch("snowflake.connector.connect")
    @patch("pandas.read_sql")
    def test_load_from_snowflake_success(self, mock_read_sql, mock_connect):
        # Mock the connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Sample data returned by the Snowflake query
        mock_data = [(1, "Alice", 100), (2, "Bob", 200)]
        mock_read_sql.return_value = pd.DataFrame(
            mock_data, columns=["id", "name", "value"]
        )

        # Test config for Snowflake connection
        config = {
            "account": "snowflake_account",
            "user": "username",
            "password": "password",
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name",
        }
        query = "SELECT * FROM users"

        # Call the function under test
        result = load_from_snowflake(config, query)

        # Assertions
        mock_connect.assert_called_once_with(
            account="snowflake_account",
            user="username",
            password="password",
            warehouse="warehouse_name",
            database="database_name",
            schema="schema_name",
            role=None,
        )
        mock_read_sql.assert_called_once_with(query, mock_connection)
        self.assertEqual(result.shape[0], 2)  # 2 rows
        self.assertEqual(result.shape[1], 3)  # 3 columns
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("snowflake.connector.connect")
    @patch("pandas.read_sql")
    def test_load_from_snowflake_with_optional_role(self, mock_read_sql, mock_connect):
        # Mock the connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Sample data returned by the Snowflake query
        mock_data = [(1, "Alice", 100), (2, "Bob", 200)]
        mock_read_sql.return_value = pd.DataFrame(
            mock_data, columns=["id", "name", "value"]
        )

        # Test config for Snowflake connection with role
        config = {
            "account": "snowflake_account",
            "user": "username",
            "password": "password",
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name",
            "role": "role_name",
        }
        query = "SELECT * FROM users"

        # Call the function under test
        result = load_from_snowflake(config, query)

        # Assertions
        mock_connect.assert_called_once_with(
            account="snowflake_account",
            user="username",
            password="password",
            warehouse="warehouse_name",
            database="database_name",
            schema="schema_name",
            role="role_name",
        )
        mock_read_sql.assert_called_once_with(query, mock_connection)
        self.assertEqual(result.shape[0], 2)
        self.assertEqual(result.shape[1], 3)
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("snowflake.connector.connect")
    @patch("pandas.read_sql")
    def test_load_from_snowflake_empty_result(self, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Return an empty result set
        mock_read_sql.return_value = pd.DataFrame(columns=["id", "name", "value"])

        # Test config for Snowflake connection
        config = {
            "account": "snowflake_account",
            "user": "username",
            "password": "password",
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name",
        }
        query = "SELECT * FROM empty_table"

        # Call the function under test
        result = load_from_snowflake(config, query)

        # Assertions
        self.assertTrue(result.empty)  # Result should be an empty DataFrame

    @patch("snowflake.connector.connect")
    def test_load_from_snowflake_missing_params(self, mock_connect):
        # Test config with missing parameters (account, user, etc.)
        config = {
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name",
        }
        query = "SELECT * FROM users"

        # Call the function under test and assert that it raises a KeyError
        with self.assertRaises(KeyError):
            load_from_snowflake(config, query)

    @patch("snowflake.connector.connect")
    @patch("pandas.read_sql")
    def test_load_from_snowflake_invalid_query(self, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Simulate an invalid SQL query
        mock_read_sql.side_effect = Exception("SQL error")

        # Test config for Snowflake connection
        config = {
            "account": "snowflake_account",
            "user": "username",
            "password": "password",
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name",
        }
        query = "INVALID SQL QUERY"

        # Call the function under test and assert that it raises an Exception
        with self.assertRaises(Exception):
            load_from_snowflake(config, query)


if __name__ == "__main__":
    unittest.main()
