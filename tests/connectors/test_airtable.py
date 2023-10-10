import unittest
import pandas 
from unittest.mock import Mock, patch
from pandasai.connectors.base import AirtableConnectorConfig
from pandasai.connectors import AirtableConnector
import requests

class TestAirTableConnector(unittest.TestCase):
    def setUp(self):

        # Define your ConnectorConfig instance here
        self.config = AirtableConnectorConfig(
            token="your_token",
            baseID="your_baseid",
            table="your_table_name"
        ).dict()

        #Create an instance of Connector 
        self.connector = AirtableConnector(config=self.config)

    @patch("requests.Session")
    def test_constructor_and_properties(self,mock_request_session):
        # Test constructor and properties
        self.assertEqual(self.connector._config,self.config)
        self.assertEqual(self.connector._session,mock_request_session)
        self.assertEqual(self.connector._session.headers, {
            "Authorization" : f"Bearer {self.config['token']}"
        })

    @patch("pandasai.connectors.AirtableConnector._connect_load")
    @patch("pandas.DataFrame")
    def test_connect_load(self,_connect_load,mock_dataframe):
        response = _connect_load(self.config)
        self.assertEqual(type(self.connector._response),mock_dataframe())
    
    @patch("pandasai.connectors.AirtableConnector.head")
    @patch("pandas.DataFrame")
    def test_head(self,mock_head,mock_dataframe):
        response = mock_head()
        self.assertEqual(type(response),mock_dataframe())
        
        