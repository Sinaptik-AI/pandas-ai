import unittest
from unittest.mock import Mock, patch

import pandas as pd

from pandasai_snowflake.snowflake import (
    SnowflakeConnector,
    SnowflakeConnectorConfig,
)
from pandasai_snowflake import load_from_snowflake


class TestSQLConnector(unittest.TestCase):
    @patch(
        "pandasai_snowflake.snowflake.create_engine",
        autospec=True,
    )
    def setUp(self, mock_create_engine):
        # Create a mock engine and connection
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        # Define your ConnectorConfig instance here
        self.config = SnowflakeConnectorConfig(
            dialect="snowflake",
            account="ehxzojy-ue47135",
            username="your_username",
            password="your_password",
            database="SNOWFLAKE_SAMPLE_DATA",
            warehouse="COMPUTED",
            dbSchema="tpch_sf1",
            table="lineitem",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        self.connector = SnowflakeConnector(self.config)

    @patch("pandasai_snowflake.snowflake.SnowflakeConnector._load_connector_config")
    @patch("pandasai_snowflake.snowflake.SnowflakeConnector._init_connection")
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties
        self.assertEqual(self.connector.config.model_dump(), self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)
        SnowflakeConnector(self.config)
        mock_load_connector_config.assert_called()
        mock_init_connection.assert_called()

    def test_repr_method(self):
        # Test __repr__ method
        expected_repr = (
            "<SnowflakeConnector dialect=snowflake "
            "Account=ehxzojy-ue47135 warehouse=COMPUTED "
            "database=SNOWFLAKE_SAMPLE_DATA schema=tpch_sf1  table=lineitem>"
        )
        self.assertEqual(repr(self.connector), expected_repr)

    def test_build_query_method(self):
        # Test _build_query method
        query = self.connector._build_query(limit=5, order="RANDOM()")
        expected_query = """SELECT * 
FROM lineitem 
WHERE column_name = :value_0 ORDER BY RANDOM() ASC
 LIMIT :param_1"""

        self.assertEqual(str(query), expected_query)

    @patch(
        "pandasai_snowflake.snowflake.pd.read_sql",
        autospec=True,
    )
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


class TestLoadFromSnowflake(unittest.TestCase):
    @patch("pandasai_snowflake.connector.connect")
    @patch("pandasai_snowflake.pd.read_sql")
    def test_load_from_snowflake(self, mock_read_sql, mock_connect):
        # Mock the connection info
        connection_info = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_db",
            "schema": "test_schema",
            "role": "test_role",
        }

        # Mock the query
        query = "SELECT * FROM test_table"

        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock the query result
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        # Call the function
        result = load_from_snowflake(connection_info, query)

        # Assert that connect was called with the correct arguments
        mock_connect.assert_called_once_with(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_db",
            schema="test_schema",
            role="test_role",
        )

        # Assert that read_sql was called with the correct arguments
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert that the result is the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("pandasai_snowflake.connector.connect")
    @patch("pandasai_snowflake.pd.read_sql")
    def test_load_from_snowflake_empty_result(self, mock_read_sql, mock_connect):
        connection_info = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_db",
            "schema": "test_schema",
            "role": "test_role",
        }

        query = "SELECT * FROM empty_table"

        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock an empty DataFrame as the query result
        expected_df = pd.DataFrame()
        mock_read_sql.return_value = expected_df

        result = load_from_snowflake(connection_info, query)

        mock_connect.assert_called_once_with(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_db",
            schema="test_schema",
            role="test_role",
        )

        mock_read_sql.assert_called_once_with(query, mock_conn)

        pd.testing.assert_frame_equal(result, expected_df)

    @patch("pandasai_snowflake.connector.connect")
    @patch("pandasai_snowflake.pd.read_sql")
    def test_load_from_snowflake_without_optional_params(
        self, mock_read_sql, mock_connect
    ):
        connection_info = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_db",
        }

        query = "SELECT * FROM test_table"

        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        result = load_from_snowflake(connection_info, query)

        mock_connect.assert_called_once_with(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_db",
            schema=None,
            role=None,
        )

        mock_read_sql.assert_called_once_with(query, mock_conn)

        pd.testing.assert_frame_equal(result, expected_df)
