import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from pandasai_bigquery import load_from_bigquery


@pytest.fixture
def mock_connection_info():
    return {
        "project_id": "test-project",
        "credentials": None,
    }


@pytest.fixture
def mock_query_result():
    # Mock query result with sample data
    return [
        {"column1": "value1", "column2": 123},
        {"column1": "value2", "column2": 456},
    ]


def test_load_from_bigquery_success(mock_connection_info, mock_query_result):
    query = "SELECT * FROM test_table"

    # Mock the BigQuery client and query job
    with patch("google.cloud.bigquery.Client") as MockBigQueryClient:
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client

        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job

        mock_query_job.result.return_value = [
            MagicMock(**row) for row in mock_query_result
        ]

        # Mock converting query results to DataFrame
        mock_dataframe = pd.DataFrame(mock_query_result)
        with patch("pandas.DataFrame", return_value=mock_dataframe):
            result = load_from_bigquery(mock_connection_info, query)

            # Assertions
            mock_client.query.assert_called_once_with(query)
            assert isinstance(result, type(mock_dataframe))
            assert result.equals(mock_dataframe)


def test_load_from_bigquery_failure(mock_connection_info):
    query = "SELECT * FROM non_existent_table"

    # Mock the BigQuery client and query job
    with patch("google.cloud.bigquery.Client") as MockBigQueryClient:
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client

        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job

        # Simulate an exception during query execution
        mock_query_job.result.side_effect = Exception("Query failed")

        with pytest.raises(Exception, match="Query failed"):
            load_from_bigquery(mock_connection_info, query)

        # Assertions
        mock_client.query.assert_called_once_with(query)
