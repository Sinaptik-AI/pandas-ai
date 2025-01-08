import unittest
from unittest.mock import patch, MagicMock
from pandasai_databricks import (
    load_from_databricks,
)


class TestDatabricksLoader(unittest.TestCase):
    @patch("databricks.sql.connect")
    def test_load_from_databricks_with_query(self, MockConnect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        MockConnect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Sample data that would be returned by Databricks SQL
        mock_cursor.fetchall.return_value = [
            (1, "Alice", 100),
            (2, "Bob", 200),
        ]
        mock_cursor.description = [("id",), ("name",), ("value",)]

        # Test config with a custom SQL query
        config = {
            "host": "databricks_host",
            "http_path": "http_path",
            "token": "access_token",
            "query": "SELECT * FROM sample_table",
        }

        # Call the function under test
        result = load_from_databricks(config)

        # Assertions
        MockConnect.assert_called_once_with(
            server_hostname="databricks_host",
            http_path="http_path",
            access_token="access_token",
        )
        mock_cursor.execute.assert_called_once_with("SELECT * FROM sample_table")
        self.assertEqual(result.shape[0], 2)  # 2 rows
        self.assertEqual(result.shape[1], 3)  # 3 columns
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("databricks.sql.connect")
    def test_load_from_databricks_with_table(self, MockConnect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        MockConnect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Sample data returned by Databricks SQL
        mock_cursor.fetchall.return_value = [
            (1, "Alice", 100),
            (2, "Bob", 200),
        ]
        mock_cursor.description = [("id",), ("name",), ("value",)]

        # Test config with a table name
        config = {
            "host": "databricks_host",
            "http_path": "http_path",
            "token": "access_token",
            "database": "test_db",
            "table": "sample_table",
        }

        # Call the function under test
        result = load_from_databricks(config)

        # Assertions
        query = "SELECT * FROM test_db.sample_table"
        mock_cursor.execute.assert_called_once_with(query)
        self.assertEqual(result.shape[0], 2)
        self.assertEqual(result.shape[1], 3)
        self.assertTrue("id" in result.columns)
        self.assertTrue("name" in result.columns)
        self.assertTrue("value" in result.columns)

    @patch("databricks.sql.connect")
    def test_load_from_databricks_no_query_or_table(self, MockConnect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        MockConnect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Test config with neither query nor table
        config = {
            "host": "databricks_host",
            "http_path": "http_path",
            "token": "access_token",
        }

        # Call the function under test and assert that it raises a ValueError
        with self.assertRaises(ValueError):
            load_from_databricks(config)

    @patch("databricks.sql.connect")
    def test_load_from_databricks_empty_result(self, MockConnect):
        # Mock the connection and cursor
        mock_connection = MagicMock()
        MockConnect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Empty result set
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("id",), ("name",), ("value",)]

        # Test config with a custom SQL query
        config = {
            "host": "databricks_host",
            "http_path": "http_path",
            "token": "access_token",
            "query": "SELECT * FROM sample_table",
        }

        # Call the function under test
        result = load_from_databricks(config)

        # Assertions
        self.assertTrue(result.empty)  # Result should be an empty DataFrame


if __name__ == "__main__":
    unittest.main()
