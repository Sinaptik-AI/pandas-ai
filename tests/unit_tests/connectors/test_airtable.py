import json
import unittest
from unittest.mock import patch

import pandas as pd

from pandasai.connectors import AirtableConnector
from pandasai.connectors.base import AirtableConnectorConfig


class TestAirTableConnector(unittest.TestCase):
    def setUp(self) -> None:
        # Define your ConnectorConfig instance here
        self.config = AirtableConnectorConfig(
            token="your_token",
            base_id="your_baseid",
            table="your_table_name",
            where=[["Status", "=", "In progress"]],
        ).dict()
        self.root_url = "https://api.airtable.com/v0/"
        self.expected_data_json = """
            {
                "records": [
                    {
                        "id": "recnAIoHRTmpecLgY",
                        "createdTime": "2023-10-09T13:04:58.000Z",
                        "fields": {
                            "Name": "Quarterly launch",
                            "Status": "Done"
                        }
                    },
                    {
                        "id": "recmRf57B2p3F9j8o",
                        "createdTime": "2023-10-09T13:04:58.000Z",
                        "fields": {
                            "Name": "Customer research",
                            "Status": "In progress"
                        }
                    },
                    {
                        "id": "recsxnHUagIce7nB2",
                        "createdTime": "2023-10-09T13:04:58.000Z",
                        "fields": {
                            "Name": "Campaign analysis",
                            "Status": "To do"
                        }
                    }
                ],
                "offset": "itrowYGFfoBEIob3C/recsxnHUagIce7nB2"
            }
            """
        # Create an instance of Connector
        self.connector = AirtableConnector(config=self.config)

    def test_constructor_and_properties(self):
        self.assertEqual(self.connector._config, self.config)
        self.assertEqual(self.connector._root_url, self.root_url)
        self.assertEqual(self.connector._cache_interval, 600)

    def test_fallback_name(self):
        self.assertEqual(self.connector.fallback_name, self.config["table"])

    @patch("requests.get")
    def test_execute(self, mock_request_get):
        mock_request_get.return_value.json.return_value = json.loads(
            self.expected_data_json
        )
        mock_request_get.return_value.status_code = 200
        execute_data = self.connector.execute()
        self.assertEqual(type(execute_data), pd.DataFrame)
        self.assertEqual(len(execute_data), 3)

    @patch("requests.get")
    def test_head(self, mock_request_get):
        mock_request_get.return_value.json.return_value = json.loads(
            self.expected_data_json
        )
        mock_request_get.return_value.status_code = 200
        execute_data = self.connector.head()
        self.assertEqual(type(execute_data), pd.DataFrame)
        self.assertLessEqual(len(execute_data), 5)

    def test_fallback_name_property(self):
        # Test fallback_name property
        fallback_name = self.connector.fallback_name
        self.assertEqual(fallback_name, self.config["table"])

    @patch("requests.get")
    def test_rows_count_property(self, mock_request_get):
        # Test rows_count property
        mock_request_get.return_value.json.return_value = json.loads(
            self.expected_data_json
        )
        mock_request_get.return_value.status_code = 200
        rows_count = self.connector.rows_count
        self.assertEqual(rows_count, 3)

    @patch("requests.get")
    def test_columns_count_property(self, mock_request_get):
        # Test columns_count property
        mock_request_get.return_value.json.return_value = json.loads(
            self.expected_data_json
        )
        mock_request_get.return_value.status_code = 200
        columns_count = self.connector.columns_count
        self.assertEqual(columns_count, 3)

    def test_build_formula_method(self):
        formula = self.connector._build_formula()
        expected_formula = "AND(Status='In progress')"
        self.assertEqual(formula, expected_formula)

    @patch("requests.get")
    def test_column_hash(self, mock_request_get):
        mock_request_get.return_value.json.return_value = json.loads(
            self.expected_data_json
        )
        mock_request_get.return_value.status_code = 200
        returned_hash = self.connector.column_hash
        self.assertEqual(
            returned_hash,
            "e4cdc9402a0831fb549d7fdeaaa089b61aeaf61e14b8a044bc027219b2db941e",
        )
