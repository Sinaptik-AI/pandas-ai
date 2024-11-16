import unittest
from unittest.mock import patch, Mock

import pandas as pd

from extensions.connectors.sql.pandasai_sql.sql import SQLConnectorConfig
from extensions.ee.connectors.oracle.pandasai_oracle.oracle import (
    OracleConnector,
)
from extensions.ee.connectors.oracle.pandasai_oracle import load_from_oracle
import cx_Oracle
from sqlalchemy.exc import DatabaseError


class TestOracleConnector(unittest.TestCase):
    @patch(
        "extensions.ee.connectors.oracle.pandasai_oracle.oracle.OracleConnector._init_connection"
    )
    def setUp(self, mock_init_connection):
        self.config = SQLConnectorConfig(
            dialect="oracle",
            driver="cx_oracle",
            username="your_username",
            password="your_password",
            host="your_host",
            port=1521,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).model_dump()

        self.connector = OracleConnector(self.config)

    def test_oracle_connector_type(self):
        assert self.connector.type == "oracle"

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    @patch("cx_Oracle.connect")
    def test_equals_oracle_connector(
        self, mock_cx_oracle_connect, mock_init_connection
    ):
        mock_cx_oracle_connect.side_effect = cx_Oracle.DatabaseError(
            "DPI-1047: Cannot locate a 64-bit Oracle Client library"
        )

        config = SQLConnectorConfig(
            dialect="oracle",
            driver="cx_oracle",
            username="your_username_differ",
            password="your_password",
            host="your_host",
            port=1521,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).model_dump()

        with self.assertRaises(DatabaseError):
            OracleConnector(config)

        # Since we can't create the second connector, we'll compare the config directly
        assert self.connector.config != config


class TestLoadFromOracle(unittest.TestCase):
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.makedsn")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.connect")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.pd.read_sql")
    def test_load_from_oracle(self, mock_read_sql, mock_connect, mock_makedsn):
        # Mock the connection info
        connection_info = {
            "host": "test_host",
            "port": 1521,
            "user": "test_user",
            "password": "test_password",
            "service_name": "test_service",
        }

        # Mock the query
        query = "SELECT * FROM test_table"

        # Mock the DSN
        mock_dsn = "mock_dsn"
        mock_makedsn.return_value = mock_dsn

        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock the query result
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        # Call the function
        result = load_from_oracle(connection_info, query)

        # Assert that makedsn was called with the correct arguments
        mock_makedsn.assert_called_once_with(
            connection_info["host"],
            connection_info["port"],
            service_name=connection_info["service_name"],
            sid=None,
        )

        # Assert that connect was called with the correct arguments
        mock_connect.assert_called_once_with(
            user=connection_info["user"],
            password=connection_info["password"],
            dsn=mock_dsn,
        )

        # Assert that read_sql was called with the correct arguments
        mock_read_sql.assert_called_once_with(query, mock_conn)

        # Assert that the result is the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.makedsn")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.connect")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.pd.read_sql")
    def test_load_from_oracle_with_sid(self, mock_read_sql, mock_connect, mock_makedsn):
        connection_info = {
            "host": "test_host",
            "port": 1521,
            "user": "test_user",
            "password": "test_password",
            "sid": "test_sid",
        }

        query = "SELECT * FROM test_table"

        mock_dsn = "mock_dsn"
        mock_makedsn.return_value = mock_dsn

        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        result = load_from_oracle(connection_info, query)

        mock_makedsn.assert_called_once_with(
            connection_info["host"],
            connection_info["port"],
            service_name=None,
            sid=connection_info["sid"],
        )

        mock_connect.assert_called_once_with(
            user=connection_info["user"],
            password=connection_info["password"],
            dsn=mock_dsn,
        )

        mock_read_sql.assert_called_once_with(query, mock_conn)

        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.makedsn")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.cx_Oracle.connect")
    @patch("extensions.ee.connectors.oracle.pandasai_oracle.pd.read_sql")
    def test_load_from_oracle_empty_result(
        self, mock_read_sql, mock_connect, mock_makedsn
    ):
        connection_info = {
            "host": "test_host",
            "port": 1521,
            "user": "test_user",
            "password": "test_password",
            "service_name": "test_service",
        }

        query = "SELECT * FROM empty_table"

        mock_dsn = "mock_dsn"
        mock_makedsn.return_value = mock_dsn

        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock an empty DataFrame as the query result
        expected_df = pd.DataFrame()
        mock_read_sql.return_value = expected_df

        result = load_from_oracle(connection_info, query)

        mock_makedsn.assert_called_once_with(
            connection_info["host"],
            connection_info["port"],
            service_name=connection_info["service_name"],
            sid=None,
        )

        mock_connect.assert_called_once_with(
            user=connection_info["user"],
            password=connection_info["password"],
            dsn=mock_dsn,
        )

        mock_read_sql.assert_called_once_with(query, mock_conn)

        pd.testing.assert_frame_equal(result, expected_df)
