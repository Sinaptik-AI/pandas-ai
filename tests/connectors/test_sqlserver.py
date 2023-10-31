import unittest
import pandas as pd
from unittest.mock import Mock, patch
from pandasai.connectors.base import SQLServerConnectorConfig
from pandasai.connectors import SQLServerConnector


class TestSQLServerConnector(unittest.TestCase):
    @patch("pandasai.connectors.sql.create_engine", autospec=True)
    def setUp(self, mock_create_engine) -> None:
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = SQLServerConnectorConfig(
            dialect="mssql",
            driver="pyodbc",
            username="your_username",
            password="your_password",
            host="your_host",
            port=1433,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
            odbc_driver="ODBC+Driver+17+for+SQL+Server",
        ).dict()

        self.connector = SQLServerConnector(self.config)

    @patch("pandasai.connectors.SQLServerConnector._load_connector_config")
    @patch("pandasai.connectors.SQLServerConnector._init_connection")
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties
        self.assertEqual(self.connector._config, self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)
        SQLServerConnector(self.config)
        mock_load_connector_config.assert_called()
        mock_init_connection.assert_called()

    def test_repr_method(self):
        # Test __repr__ method
        expected_repr = (
            "<SQLServerConnector dialect=mssql driver=pyodbc host=your_host "
            "port=1433 database=your_database table=your_table>"
        )
        self.assertEqual(repr(self.connector), expected_repr)

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
        mock_df = Mock()
        mock_df.columns = ["Column1", "Column2"]
        self.connector.head = Mock(return_value=mock_df)
        columns_count = self.connector.columns_count
        self.assertEqual(columns_count, 2)

    def test_column_hash_property(self):
        # Test column_hash property
        mock_df = Mock()
        mock_df.columns = ["Column1", "Column2"]
        self.connector.head = Mock(return_value=mock_df)
        column_hash = self.connector.column_hash
        self.assertIsNotNone(column_hash)
        self.assertEqual(
            column_hash,
            "ea6a80582b83e1511f8be83412b13e7b86d20c45b96fcf9731f3b99dc3b568aa",
        )

    def test_fallback_name_property(self):
        # Test fallback_name property
        fallback_name = self.connector.fallback_name
        self.assertEqual(fallback_name, "your_table")
