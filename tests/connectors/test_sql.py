import unittest
import pandas as pd
from unittest.mock import Mock, patch
from pandasai.connectors.base import ConnectorConfig
from pandasai.connectors.sql import SQLConnector


class TestSQLConnector(unittest.TestCase):
    @patch("pandasai.connectors.sql.create_engine", autospec=True)
    @patch("pandasai.connectors.sql.sql", autospec=True)
    def setUp(self, mock_sql, mock_create_engine):
        # Create a mock engine and connection
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        # Define your ConnectorConfig instance here
        self.config = ConnectorConfig(
            dialect="mysql",
            driver="pymysql",
            username="your_username",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        self.connector = SQLConnector(self.config)

    def test_constructor_and_properties(self):
        # Test constructor and properties
        self.assertEqual(self.connector._config, self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)

    def test_repr_method(self):
        # Test __repr__ method
        expected_repr = (
            "<SQLConnector dialect=mysql driver=pymysql "
            "username=your_username password=your_password "
            "host=your_host port=443 database=your_database table=your_table>"
        )
        self.assertEqual(repr(self.connector), expected_repr)

    def test_build_query_method(self):
        # Test _build_query method
        query = self.connector._build_query(limit=5, order="RAND()")
        expected_query = (
            "SELECT * FROM your_table WHERE column_name = 'value' "
            "ORDER BY RAND() LIMIT 5"
        )
        self.assertEqual(str(query), expected_query)

    @patch("pandasai.connectors.sql.pd.read_sql", autospec=True)
    def test_head_method(self, mock_read_sql):
        expected_data = pd.DataFrame({"Column1": [1, 2, 3], "Column2": [4, 5, 6]})
        mock_read_sql.return_value = expected_data
        head_data = self.connector.head()
        pd.testing.assert_frame_equal(head_data, expected_data)

    def test_rows_count_property(self):
        # Test rows_count property
        self.connector._rows_count = None
        self.mock_connection.execute.return_value.fetchone.return_value = (
            50,
        )  # Sample rows count
        rows_count = self.connector.rows_count
        self.assertEqual(rows_count, 50)

    def test_columns_count_property(self):
        # Test columns_count property
        self.connector._columns_count = None
        self.mock_connection.execute.return_value.fetchone.return_value = (
            8,
        )  # Sample columns count
        columns_count = self.connector.columns_count
        self.assertEqual(columns_count, 8)

    def test_column_hash_property(self):
        # Test column_hash property
        mock_df = Mock()
        mock_df.columns = ["Column1", "Column2"]
        self.connector.head = Mock(return_value=mock_df)
        column_hash = self.connector.column_hash
        self.assertIsNotNone(column_hash)

    def test_fallback_name_property(self):
        # Test fallback_name property
        fallback_name = self.connector.fallback_name
        self.assertEqual(fallback_name, "your_table")
