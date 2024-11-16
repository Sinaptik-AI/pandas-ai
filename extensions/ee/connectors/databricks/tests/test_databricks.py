import unittest
from unittest.mock import Mock, patch

import pandas as pd

from pandasai_databricks.databricks import (
    DatabricksConnector,
    DatabricksConnectorConfig,
)


class TestDataBricksConnector(unittest.TestCase):
    @patch("pandasai_databricks.databricks.sql")
    def setUp(self, mock_sql):
        # Create mock connection and cursor
        self.mock_cursor = Mock()
        self.mock_connection = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        mock_sql.connect.return_value = self.mock_connection

        # Define your ConnectorConfig instance here
        self.config = DatabricksConnectorConfig(
            dialect="databricks",
            host="ehxzojy-ue47135",
            token="token",
            database="DATABRICKS_SAMPLE_DATA",
            http_path="/sql/1.0/warehouses/1241rsa32",
            table="lineitem",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of DatabricksConnector
        self.connector = DatabricksConnector(self.config)

    def test_constructor_and_properties(self):
        self.assertEqual(self.connector.config.model_dump(), self.config)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cursor, self.mock_cursor)
        self.assertEqual(self.connector._cache_interval, 600)

    def test_repr_method(self):
        expected_repr = (
            "<DatabricksConnector dialect=databricks "
            "host=ehxzojy-ue47135 "
            "database=DATABRICKS_SAMPLE_DATA http_path=/sql/1.0/warehouses/1241rsa32"
        )
        self.assertEqual(repr(self.connector), expected_repr)

    def test_build_query_method(self):
        query = self.connector._build_query(limit=5, order="RAND()")
        expected_query = """SELECT * FROM DATABRICKS_SAMPLE_DATA.lineitem WHERE column_name = 'value' ORDER BY RAND() ASC LIMIT 5"""
        self.assertEqual(query, expected_query)

    def test_head_method(self):
        # Mock cursor response
        mock_data = [(1, 4), (2, 5), (3, 6)]
        self.mock_cursor.fetchall.return_value = mock_data
        self.mock_cursor.description = [("Column1", None), ("Column2", None)]

        expected_data = pd.DataFrame(mock_data, columns=["Column1", "Column2"])
        head_data = self.connector.head()
        pd.testing.assert_frame_equal(head_data, expected_data)

    def test_execute_query_with_params(self):
        query = "SELECT * FROM table WHERE id = :id"
        params = {"id": 123}
        expected_query = "SELECT * FROM table WHERE id = 123"

        # Mock cursor response
        mock_data = [(1, "test")]
        self.mock_cursor.fetchall.return_value = mock_data
        self.mock_cursor.description = [("id", None), ("name", None)]

        self.connector._execute_query(query, params)
        self.mock_cursor.execute.assert_called_with(expected_query)

    def test_close_method(self):
        self.connector.close()
        self.mock_cursor.close.assert_called_once()
        self.mock_connection.close.assert_called_once()
