import unittest
from unittest.mock import Mock, patch

import pandas as pd

from extensions.ee.connectors.databricks.pandasai_databricks.databricks import (
    DatabricksConnector,
    DatabricksConnectorConfig,
)
from extensions.ee.connectors.databricks.pandasai_databricks import load_from_databricks


class TestDataBricksConnector(unittest.TestCase):
    @patch(
        "extensions.ee.connectors.databricks.pandasai_databricks.databricks.create_engine",
        autospec=True,
    )
    # @patch("pandasai.connectors.sql.sql", autospec=True)
    def setUp(self, mock_create_engine):
        # Create a mock engine and connection
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        # Define your ConnectorConfig instance here
        self.config = DatabricksConnectorConfig(
            dialect="databricks",
            host="ehxzojy-ue47135",
            port=443,
            token="token",
            database="DATABRICKS_SAMPLE_DATA",
            httpPath="/sql/1.0/warehouses/1241rsa32",
            table="lineitem",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        self.connector = DatabricksConnector(self.config)

    @patch(
        "extensions.ee.connectors.databricks.pandasai_databricks.databricks.DatabricksConnector._load_connector_config"
    )
    @patch(
        "extensions.ee.connectors.databricks.pandasai_databricks.databricks.DatabricksConnector._init_connection"
    )
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties

        mock_load_connector_config.return_value = self.config
        self.assertEqual(self.connector.config.model_dump(), self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)
        DatabricksConnector(self.config)
        mock_load_connector_config.assert_called()
        mock_init_connection.assert_called()

    def test_repr_method(self):
        # Test __repr__ method

        expected_repr = (
            "<DatabricksConnector dialect=databricks "
            "host=ehxzojy-ue47135 port=443 "
            "database=DATABRICKS_SAMPLE_DATA httpPath=/sql/1.0/warehouses/1241rsa32"
        )
        self.assertEqual(repr(self.connector), expected_repr)

    def test_build_query_method(self):
        # Test _build_query method
        query = self.connector._build_query(limit=5, order="RAND()")
        expected_query = """SELECT * 
FROM lineitem 
WHERE column_name = :value_0 ORDER BY RAND() ASC
 LIMIT :param_1"""
        self.assertEqual(str(query), expected_query)

    @patch("extensions.connectors.sql.pandasai_sql.sql.pd.read_sql", autospec=True)
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
        self.assertEqual(fallback_name, "lineitem")


class TestLoadFromDatabricks(unittest.TestCase):
    @patch("extensions.ee.connectors.databricks.pandasai_databricks.sql.connect")
    def test_load_from_databricks(self, mock_connect):
        # Mock the connection info
        connection_info = {
            "server_hostname": "test_hostname",
            "http_path": "test_path",
            "access_token": "test_token",
        }

        # Mock the query
        query = "SELECT * FROM test_table"

        # Mock the cursor and its methods
        mock_cursor = Mock()
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock the query result
        mock_cursor.fetchall.return_value = [(1, "a"), (2, "b")]
        mock_cursor.description = [("col1", None), ("col2", None)]

        # Call the function
        result = load_from_databricks(connection_info, query)

        # Assert that connect was called with the correct arguments
        mock_connect.assert_called_once_with(
            server_hostname="test_hostname",
            http_path="test_path",
            access_token="test_token",
        )

        # Assert that execute was called with the correct query
        mock_cursor.execute.assert_called_once_with(query)

        # Assert that the result is the expected DataFrame
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.databricks.pandasai_databricks.sql.connect")
    def test_load_from_databricks_empty_result(self, mock_connect):
        connection_info = {
            "server_hostname": "test_hostname",
            "http_path": "test_path",
            "access_token": "test_token",
        }

        query = "SELECT * FROM empty_table"

        mock_cursor = Mock()
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock an empty result
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("col1", None), ("col2", None)]

        result = load_from_databricks(connection_info, query)

        mock_connect.assert_called_once_with(
            server_hostname="test_hostname",
            http_path="test_path",
            access_token="test_token",
        )

        mock_cursor.execute.assert_called_once_with(query)

        expected_df = pd.DataFrame(columns=["col1", "col2"])
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.databricks.pandasai_databricks.sql.connect")
    def test_load_from_databricks_connection_error(self, mock_connect):
        connection_info = {
            "server_hostname": "test_hostname",
            "http_path": "test_path",
            "access_token": "test_token",
        }

        query = "SELECT * FROM test_table"

        # Simulate a connection error
        mock_connect.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception) as context:
            load_from_databricks(connection_info, query)

        self.assertTrue("Connection failed" in str(context.exception))

        mock_connect.assert_called_once_with(
            server_hostname="test_hostname",
            http_path="test_path",
            access_token="test_token",
        )
