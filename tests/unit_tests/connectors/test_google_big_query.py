import unittest
from unittest.mock import Mock, patch

import pandas as pd

from extensions.connectors.sql.pandasai_sql.sql import PostgreSQLConnector
from extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query import (
    GoogleBigQueryConnector,
    GoogleBigQueryConnectorConfig,
)
from extensions.ee.connectors.bigquery.pandasai_bigquery import load_from_bigquery


class TestGoogleBigQueryConnector(unittest.TestCase):
    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.create_engine",
        autospec=True,
    )
    def setUp(self, mock_create_engine) -> None:
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database",
            table="yourtable",
            credentials_path="keyfile.json",
            projectID="project_id",
        ).dict()

        self.connector = GoogleBigQueryConnector(self.config)

    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.GoogleBigQueryConnector._load_connector_config"
    )
    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.GoogleBigQueryConnector._init_connection"
    )
    def test_constructor_and_properties(
        self, mock_load_connector_config, mock_init_connection
    ):
        # Test constructor and properties
        self.assertEqual(self.connector.config.model_dump(), self.config)
        self.assertEqual(self.connector._engine, self.mock_engine)
        self.assertEqual(self.connector._connection, self.mock_connection)
        self.assertEqual(self.connector._cache_interval, 600)
        GoogleBigQueryConnector(self.config)
        mock_load_connector_config.assert_called()
        mock_init_connection.assert_called()

    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.create_engine",
        autospec=True,
    )
    def test_constructor_and_properties_with_base64_string(self, mock_create_engine):
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database",
            table="yourtable",
            credentials_base64="base64_str",
            projectID="project_id",
        ).dict()

        self.connector = GoogleBigQueryConnector(self.config)
        mock_create_engine.assert_called_with(
            "bigquery://project_id/database?credentials_base64=base64_str"
        )

    def test_repr_method(self):
        # Test __repr__ method
        expected_repr = (
            "<GoogleBigQueryConnector dialect=bigquery "
            "projectid= project_id database=database >"
        )
        self.assertEqual(repr(self.connector), expected_repr)

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
            "0d045cff164deef81e24b0ed165b7c9c2789789f013902115316cde9d214fe63",
        )

    def test_fallback_name_property(self):
        # Test fallback_name property
        fallback_name = self.connector.fallback_name
        self.assertEqual(fallback_name, "yourtable")

    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.create_engine",
        autospec=True,
    )
    def test_constructor_and_properties_equal_func(self, mock_create_engine):
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database",
            table="yourtable",
            credentials_base64="base64_str",
            projectID="project_id",
        ).dict()

        self.connector = GoogleBigQueryConnector(self.config)
        connector_2 = GoogleBigQueryConnector(self.config)

        assert self.connector.equals(connector_2)

    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.create_engine",
        autospec=True,
    )
    def test_constructor_and_properties_not_equal_func(self, mock_create_engine):
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database",
            table="yourtable",
            credentials_base64="base64_str",
            projectID="project_id",
        ).dict()

        config2 = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database2",
            table="yourtable",
            credentials_base64="base64_str",
            projectID="project_id",
        ).dict()

        self.connector = GoogleBigQueryConnector(self.config)
        connector_2 = GoogleBigQueryConnector(config2)

        assert not self.connector.equals(connector_2)

    @patch(
        "extensions.ee.connectors.bigquery.pandasai_bigquery.google_big_query.create_engine",
        autospec=True,
    )
    @patch("extensions.connectors.sql.pandasai_sql.SQLConnector._init_connection")
    def test_constructor_and_properties_different_type(
        self, mock_connection, mock_create_engine
    ):
        self.mock_engine = Mock()
        self.mock_connection = Mock()
        self.mock_engine.connect.return_value = self.mock_connection
        mock_create_engine.return_value = self.mock_engine

        self.config = GoogleBigQueryConnectorConfig(
            dialect="bigquery",
            database="database",
            table="yourtable",
            credentials_base64="base64_str",
            projectID="project_id",
        ).dict()

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

        self.connector = GoogleBigQueryConnector(self.config)

        assert not self.connector.equals(connector_2)


class TestLoadFromBigQuery(unittest.TestCase):
    @patch("extensions.ee.connectors.bigquery.pandasai_bigquery.bigquery.Client")
    def test_load_from_bigquery(self, mock_client):
        # Mock the connection info
        connection_info = {
            "project_id": "test_project",
            "credentials": "test_credentials",
        }

        # Mock the query
        query = "SELECT * FROM test_table"

        # Mock the query job and its result
        mock_query_job = Mock()
        mock_result = [{"col1": 1, "col2": "a"}, {"col1": 2, "col2": "b"}]
        mock_query_job.result.return_value = mock_result

        # Set up the mock client to return our mock query job
        mock_client_instance = mock_client.return_value
        mock_client_instance.query.return_value = mock_query_job

        # Call the function
        result = load_from_bigquery(connection_info, query)

        # Assert that the client was created with the correct arguments
        mock_client.assert_called_once_with(
            project=connection_info["project_id"],
            credentials=connection_info["credentials"],
        )

        # Assert that the query was executed
        mock_client_instance.query.assert_called_once_with(query)

        # Assert that the result is a pandas DataFrame with the expected data
        expected_df = pd.DataFrame(mock_result)
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.bigquery.pandasai_bigquery.bigquery.Client")
    def test_load_from_bigquery_without_credentials(self, mock_client):
        # Mock the connection info without credentials
        connection_info = {"project_id": "test_project"}

        query = "SELECT * FROM test_table"

        mock_query_job = Mock()
        mock_result = [{"col1": 1, "col2": "a"}, {"col1": 2, "col2": "b"}]
        mock_query_job.result.return_value = mock_result

        mock_client_instance = mock_client.return_value
        mock_client_instance.query.return_value = mock_query_job

        result = load_from_bigquery(connection_info, query)

        # Assert that the client was created with the correct arguments
        mock_client.assert_called_once_with(
            project=connection_info["project_id"], credentials=None
        )

        mock_client_instance.query.assert_called_once_with(query)

        expected_df = pd.DataFrame(mock_result)
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("extensions.ee.connectors.bigquery.pandasai_bigquery.bigquery.Client")
    def test_load_from_bigquery_empty_result(self, mock_client):
        connection_info = {
            "project_id": "test_project",
            "credentials": "test_credentials",
        }

        query = "SELECT * FROM empty_table"

        mock_query_job = Mock()
        mock_result = []  # Empty result
        mock_query_job.result.return_value = mock_result

        mock_client_instance = mock_client.return_value
        mock_client_instance.query.return_value = mock_query_job

        result = load_from_bigquery(connection_info, query)

        mock_client.assert_called_once_with(
            project=connection_info["project_id"],
            credentials=connection_info["credentials"],
        )

        mock_client_instance.query.assert_called_once_with(query)

        expected_df = pd.DataFrame()  # Empty DataFrame
        pd.testing.assert_frame_equal(result, expected_df)
