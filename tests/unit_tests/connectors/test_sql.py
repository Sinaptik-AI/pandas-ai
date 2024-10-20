import unittest
from unittest.mock import Mock, patch

import pandas as pd

from extensions.connectors.sql.pandasai_sql import (
    SQLConnector,
    SQLConnectorConfig,
    load_from_mysql,
    load_from_postgres,
)
from extensions.connectors.sql.pandasai_sql.sql import (
    PostgreSQLConnector,
    MySQLConnector,
)
from pandasai.exceptions import MaliciousQueryError


class TestSQLConnector(unittest.TestCase):
    @patch("extensions.connectors.sql.pandasai_sql.sql.create_engine", autospec=True)
    def setUp(self, mock_create_engine):
        # Create a mock engine and connection
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
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

    @patch(
        "extensions.connectors.sql.pandasai_sql.sql.SQLConnector._load_connector_config"
    )
    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties

        self.assertEqual(self.connector.config.model_dump(), self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)
        SQLConnector(self.config)
        mock_load_connector_config.assert_called()
        mock_init_connection.assert_called()

    def test_repr_method(self):
        # Test __repr__ method
        expected_repr = (
            "<SQLConnector dialect=mysql driver=pymysql "
            "host=your_host port=443 database=your_database table=your_table>"
        )
        self.assertEqual(repr(self.connector), expected_repr)

    def test_build_query_method(self):
        # Test _build_query method
        query = self.connector._build_query(limit=5, order="RAND()")
        expected_query = """SELECT * 
FROM your_table 
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
        self.assertEqual(fallback_name, "your_table")

    def test_is_sql_query_safe_safe_query(self):
        safe_query = "SELECT * FROM users WHERE username = 'John'"
        result = self.connector._is_sql_query_safe(safe_query)
        assert result is True

    def test_is_sql_query_safe_malicious_query(self):
        malicious_query = "DROP TABLE users"
        result = self.connector._is_sql_query_safe(malicious_query)
        assert result is False

    @patch("extensions.connectors.sql.pandasai_sql.sql.pd.read_sql", autospec=True)
    def test_execute_direct_sql_query_safe_query(self, mock_sql):
        safe_query = "SELECT * FROM users WHERE username = 'John'"
        expected_data = pd.DataFrame({"Column1": [1, 2, 3], "Column2": [4, 5, 6]})
        mock_sql.return_value = expected_data
        result = self.connector.execute_direct_sql_query(safe_query)
        assert isinstance(result, pd.DataFrame)

    def test_execute_direct_sql_query_malicious_query(self):
        malicious_query = "DROP TABLE users"
        try:
            self.connector.execute_direct_sql_query(malicious_query)
            assert False, "MaliciousQueryError not raised"
        except MaliciousQueryError:
            pass

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_equals_identical_configs(self, mock_init_connection):
        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
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
        connector_2 = SQLConnector(self.config)

        assert self.connector.equals(connector_2)

    @patch(
        "extensions.connectors.sql.pandasai_sql.sql.SQLConnector._load_connector_config"
    )
    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_equals_different_configs(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
            dialect="mysql",
            driver="pymysql",
            username="your_username_differ",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        connector_2 = SQLConnector(self.config)

        assert not self.connector.equals(connector_2)

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_equals_different_connector(self, mock_init_connection):
        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
            dialect="postgresql",
            driver="psycopg2",
            username="your_username_differ",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        connector_2 = PostgreSQLConnector(self.config)

        assert not self.connector.equals(connector_2)

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_equals_connector_type(self, mock_init_connection):
        # Define your ConnectorConfig instance here
        config = {
            "username": "your_username_differ",
            "password": "your_password",
            "host": "your_host",
            "port": 443,
            "database": "your_database",
            "table": "your_table",
            "where": [["column_name", "=", "value"]],
        }

        # Create an instance of SQLConnector
        connector_2 = PostgreSQLConnector(config)

        assert connector_2.type == "postgresql"

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    def test_equals_sql_connector_type(self, mock_init_connection):
        # Define your ConnectorConfig instance here

        config = {
            "username": "your_username_differ",
            "password": "your_password",
            "host": "your_host",
            "port": 443,
            "database": "your_database",
            "table": "your_table",
            "where": [["column_name", "=", "value"]],
        }

        # Create an instance of SQLConnector
        connector_2 = MySQLConnector(config)

        assert connector_2.type == "mysql"

    @patch("extensions.connectors.sql.pandasai_sql.sql.create_engine", autospec=True)
    def test_connector_constructor_with_ssl_settings(self, create_engine_mock):
        config = SQLConnectorConfig(
            dialect="mysql",
            driver="pymysql",
            username="your_username",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            connect_args={"sslmode": "require", "sslrootcert": None},
            where=[["column_name", "=", "value"]],
        ).dict()
        SQLConnector(config)
        create_engine_mock.assert_called_with(
            "mysql+pymysql://your_username:your_password@your_host:443/your_database",
            connect_args={"sslmode": "require", "sslrootcert": None},
        )

    @patch("extensions.connectors.sql.pandasai_sql.sql.create_engine", autospec=True)
    def test_connector_constructor_with_no_ssl_settings(self, create_engine_mock):
        config = SQLConnectorConfig(
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
        SQLConnector(config)
        create_engine_mock.assert_called_with(
            "mysql+pymysql://your_username:your_password@your_host:443/your_database",
            connect_args={},
        )

    @patch("extensions.connectors.sql.pandasai_sql.sql.SQLConnector._init_connection")
    @patch("extensions.connectors.sql.pandasai_sql.sql.pd.read_sql")
    def test_equals_connector_execute_direct_sql(
        self, mock_read_sql, mock_init_connection
    ):
        # Define your ConnectorConfig instance here
        config = {
            "username": "your_username_differ",
            "password": "your_password",
            "host": "your_host",
            "port": 443,
            "database": "your_database",
            "table": "your_table",
            "where": [["column_name", "=", "value"]],
        }

        # Create an instance of SQLConnector
        connector_2 = PostgreSQLConnector(config)

        connector_2.execute_direct_sql_query("SELECT * from `orders`")

        mock_read_sql.assert_called_once()


class TestSQLLoaders(unittest.TestCase):
    def setUp(self):
        self.connection_info = {
            "host": "localhost",
            "user": "testuser",
            "password": "testpass",
            "database": "testdb",
            "port": 3306,
        }
        self.query = "SELECT * FROM test_table"

    @patch("extensions.connectors.sql.pandasai_sql.pd.read_sql")
    def test_load_from_mysql(self, mock_read_sql):
        mock_pymysql = Mock()
        mock_connection = Mock()
        mock_pymysql.connect.return_value = mock_connection

        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        with patch.dict("sys.modules", {"pymysql": mock_pymysql}):
            result = load_from_mysql(self.connection_info, self.query)

        mock_pymysql.connect.assert_called_once_with(
            host=self.connection_info["host"],
            user=self.connection_info["user"],
            password=self.connection_info["password"],
            database=self.connection_info["database"],
            port=self.connection_info["port"],
        )
        mock_read_sql.assert_called_once_with(self.query, mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.connectors.sql.pandasai_sql.pd.read_sql")
    def test_load_from_postgres(self, mock_read_sql):
        mock_psycopg2 = Mock()
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection

        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_sql.return_value = expected_df

        with patch.dict("sys.modules", {"psycopg2": mock_psycopg2}):
            result = load_from_postgres(self.connection_info, self.query)

        mock_psycopg2.connect.assert_called_once_with(
            host=self.connection_info["host"],
            user=self.connection_info["user"],
            password=self.connection_info["password"],
            dbname=self.connection_info["database"],
            port=self.connection_info["port"],
        )
        mock_read_sql.assert_called_once_with(self.query, mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
