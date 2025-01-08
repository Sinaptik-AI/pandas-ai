import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pandasai_oracle import load_from_oracle


class TestOracleLoader(unittest.TestCase):
    @patch("cx_Oracle.connect")
    @patch("pandas.read_sql")
    @patch("cx_Oracle.makedsn")
    def test_load_from_oracle_success(self, mock_makedsn, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_makedsn.return_value = "oracle_host:1521/orcl_service"

        # Sample data returned by the Oracle query
        mock_data = [(1, "Alice", 100), (2, "Bob", 200)]
        mock_read_sql.return_value = pd.DataFrame(
            mock_data, columns=["id", "name", "value"]
        )

        # Test config for Oracle connection
        config = {
            "host": "oracle_host",
            "port": 1521,
            "service_name": "orcl_service",
            "user": "username",
            "password": "password",
        }
        query = "SELECT * FROM users"

        # Call the function under test
        result = load_from_oracle(config, query)

        # Assertions
        mock_connect.assert_called_once_with(
            user="username",
            password="password",
            dsn="oracle_host:1521/orcl_service",
        )
        mock_read_sql.assert_called_once_with(query, mock_connection)
        self.assertEqual(result.shape[0], 2)  # 2 rows
        self.assertEqual(result.shape[1], 3)  # 3 columns
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("cx_Oracle.connect")
    @patch("pandas.read_sql")
    @patch("cx_Oracle.makedsn")
    def test_load_from_oracle_with_sid(self, mock_makedsn, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_makedsn.return_value = "oracle_host:1521/orcl_sid"

        # Sample data returned by the Oracle query
        mock_data = [(1, "Alice", 100), (2, "Bob", 200)]
        mock_read_sql.return_value = pd.DataFrame(
            mock_data, columns=["id", "name", "value"]
        )

        # Test config with SID instead of service_name
        config = {
            "host": "oracle_host",
            "port": 1521,
            "sid": "orcl_sid",
            "user": "username",
            "password": "password",
        }
        query = "SELECT * FROM users"

        # Call the function under test
        result = load_from_oracle(config, query)

        # Assertions
        mock_connect.assert_called_once_with(
            user="username",
            password="password",
            dsn="oracle_host:1521/orcl_sid",
        )
        mock_read_sql.assert_called_once_with(query, mock_connection)
        self.assertEqual(result.shape[0], 2)
        self.assertEqual(result.shape[1], 3)
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("cx_Oracle.connect")
    @patch("pandas.read_sql")
    def test_load_from_oracle_empty_result(self, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Return an empty result set
        mock_read_sql.return_value = pd.DataFrame(columns=["id", "name", "value"])

        # Test config for Oracle connection
        config = {
            "host": "oracle_host",
            "port": 1521,
            "service_name": "orcl_service",
            "user": "username",
            "password": "password",
        }
        query = "SELECT * FROM empty_table"

        # Call the function under test
        result = load_from_oracle(config, query)

        # Assertions
        self.assertTrue(result.empty)  # Result should be an empty DataFrame

    @patch("cx_Oracle.connect")
    def test_load_from_oracle_missing_params(self, mock_connect):
        # Test config with missing parameters (host, user, etc.)
        config = {
            "port": 1521,
            "service_name": "orcl_service",
            "password": "password",
        }
        query = "SELECT * FROM users"

        # Call the function under test and assert that it raises a KeyError
        with self.assertRaises(KeyError):
            load_from_oracle(config, query)

    @patch("cx_Oracle.connect")
    @patch("pandas.read_sql")
    def test_load_from_oracle_invalid_query(self, mock_read_sql, mock_connect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Simulate an invalid SQL query
        mock_read_sql.side_effect = Exception("SQL error")

        # Test config for Oracle connection
        config = {
            "host": "oracle_host",
            "port": 1521,
            "service_name": "orcl_service",
            "user": "username",
            "password": "password",
        }
        query = "INVALID SQL QUERY"

        # Call the function under test and assert that it raises an Exception
        with self.assertRaises(Exception):
            load_from_oracle(config, query)


if __name__ == "__main__":
    unittest.main()
