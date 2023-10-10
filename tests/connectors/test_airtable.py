import unittest
import pandas as pd
from unittest.mock import Mock, patch
from pandasai.connectors.base import AirtableConnectorConfig
from pandasai.connectors import AirtableConnector


class TestAirTableConnector(unittest.TestCase):
    def setUp(self):
        # Define your ConnectorConfig instance here
        self.config = AirtableConnectorConfig(
            token="your_token", baseID="your_baseid", table="your_table_name"
        ).dict()
        self.root_url = "https://api.airtable.com/v0/"
        # Create an instance of Connector
        self.connector = AirtableConnector(config=self.config)

    def test_constructor_and_properties(self):
        self.assertEqual(self.connector._config, self.config)
        self.assertEqual(self.connector._root_url, self.root_url)

    def test_execute(self):
        expected_data_json = {
            "records": [
                {
                    "id": "recnAIoHRTmpecLgY",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Quarterly launch", "Status": "Done"},
                },
                {
                    "id": "recmRf57B2p3F9j8o",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Customer research", "Status": "In progress"},
                },
                {
                    "id": "recsxnHUagIce7nB2",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Campaign analysis", "Status": "To do"},
                },
            ],
            "offset": "itrowYGFfoBEIob3C/recsxnHUagIce7nB2",
        }
        print(expected_data_json)
        records = [
            {"id": record["id"], **record["fields"]}
            for record in expected_data_json["records"]
        ]
        expected_data = pd.DataFrame(records)
        self.connector.execute = Mock(return_value=expected_data)
        execute_data = self.connector.execute()
        self.assertEqual(execute_data.equals(expected_data), True)

    def test_head(self):
        expected_data_json = {
            "records": [
                {
                    "id": "recnAIoHRTmpecLgY",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Quarterly launch", "Status": "Done"},
                },
                {
                    "id": "recmRf57B2p3F9j8o",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Customer research", "Status": "In progress"},
                },
                {
                    "id": "recsxnHUagIce7nB2",
                    "createdTime": "2023-10-09T13:04:58.000Z",
                    "fields": {"Name": "Campaign analysis", "Status": "To do"},
                },
            ],
            "offset": "itrowYGFfoBEIob3C/recsxnHUagIce7nB2",
        }

        records = [
            {"id": record["id"], **record["fields"]}
            for record in expected_data_json["records"]
        ]
        expected_data = pd.DataFrame(records)
        self.connector.head = Mock(return_value=expected_data)
        head_data = self.connector.head()

        self.assertEqual(head_data.equals(expected_data), True)
        self.assertLessEqual(len(head_data), 5)
