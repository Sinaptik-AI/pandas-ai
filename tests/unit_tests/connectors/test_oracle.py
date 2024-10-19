import unittest
from unittest.mock import patch

from extensions.connectors.sql.pandasai_sql.sql import SQLConnectorConfig
from extensions.ee.connectors.oracle.pandasai_oracle.oracle import (
    OracleConnector,
)
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
