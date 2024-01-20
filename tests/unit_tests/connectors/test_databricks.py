import unittest
from unittest.mock import Mock, patch

import pandas as pd

from pandasai.connectors import DatabricksConnector
from pandasai.connectors.base import DatabricksConnectorConfig


class TestDataBricksConnector(unittest.TestCase):
    @patch("pandasai.connectors.databricks.create_engine", autospec=True)
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

    @patch("pandasai.connectors.DatabricksConnector._load_connector_config")
    @patch("pandasai.connectors.DatabricksConnector._init_connection")
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties

        mock_load_connector_config.return_value = self.config
        self.assertEqual(self.connector._config, self.config)
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
        self.assertEqual(fallback_name, "lineitem")
