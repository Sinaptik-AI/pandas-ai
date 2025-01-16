import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

# Assuming the functions are in a module called db_loader
from pandasai_sql import (
    load_from_cockroachdb,
    load_from_mysql,
    load_from_postgres,
    load_from_sqlite,
)


class TestDatabaseLoader(unittest.TestCase):
    @patch("pymysql.connect")
    @patch("pandas.read_sql")
    def test_load_from_mysql(self, mock_read_sql, mock_pymysql_connect):
        # Setup the mock return values
        mock_conn = MagicMock()
        mock_pymysql_connect.return_value = mock_conn
        mock_read_sql.return_value = pd.DataFrame(
            {"column1": [1, 2], "column2": [3, 4]}
        )

        # Test data
        connection_info = {
            "host": "localhost",
            "user": "root",
            "password": "password",
            "database": "test_db",
            "port": 3306,
        }
        query = "SELECT * FROM test_table"

        result = load_from_mysql(connection_info, query)

        # Assert that the connection is made and SQL query is executed
        mock_pymysql_connect.assert_called_once_with(
            host="localhost",
            user="root",
            password="password",
            database="test_db",
            port=3306,
        )
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 2))

    @patch("psycopg2.connect")
    @patch("pandas.read_sql")
    def test_load_from_postgres(self, mock_read_sql, mock_psycopg2_connect):
        # Setup the mock return values
        mock_conn = MagicMock()
        mock_psycopg2_connect.return_value = mock_conn
        mock_read_sql.return_value = pd.DataFrame(
            {"column1": [5, 6], "column2": [7, 8]}
        )

        # Test data
        connection_info = {
            "host": "localhost",
            "user": "postgres",
            "password": "password",
            "database": "test_db",
            "port": 5432,
        }
        query = "SELECT * FROM test_table"

        result = load_from_postgres(connection_info, query)

        # Assert that the connection is made and SQL query is executed
        mock_psycopg2_connect.assert_called_once_with(
            host="localhost",
            user="postgres",
            password="password",
            dbname="test_db",
            port=5432,
        )
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 2))

    @patch("sqlite3.connect")
    @patch("pandas.read_sql")
    def test_load_from_sqlite(self, mock_read_sql, mock_sqlite3_connect):
        # Setup the mock return values
        mock_conn = MagicMock()
        mock_sqlite3_connect.return_value = mock_conn
        mock_read_sql.return_value = pd.DataFrame(
            {"column1": [9, 10], "column2": [11, 12]}
        )

        # Test data
        connection_info = {"database": "test_db.sqlite"}
        query = "SELECT * FROM test_table"

        result = load_from_sqlite(connection_info, query)

        # Assert that the connection is made and SQL query is executed
        mock_sqlite3_connect.assert_called_once_with("test_db.sqlite")
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 2))

    @patch("psycopg2.connect")
    @patch("pandas.read_sql")
    def test_load_from_cockroachdb(self, mock_read_sql, mock_postgresql_connect):
        # Setup the mock return values
        mock_conn = MagicMock()
        mock_postgresql_connect.return_value = mock_conn
        mock_read_sql.return_value = pd.DataFrame(
            {"column1": [13, 14], "column2": [15, 16]}
        )

        # Test data
        connection_info = {
            "host": "localhost",
            "user": "root",
            "password": "password",
            "database": "test_db",
            "port": 26257,
        }
        query = "SELECT * FROM test_table"

        result = load_from_cockroachdb(connection_info, query)

        # Assert that the connection is made and SQL query is executed
        mock_postgresql_connect.assert_called_once_with(
            host="localhost",
            user="root",
            password="password",
            dbname="test_db",
            port=26257,
        )
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 2))


if __name__ == "__main__":
    unittest.main()
