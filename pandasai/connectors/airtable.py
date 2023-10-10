"""
Airtable connectors are used to connect airtable records.
"""

from .base import AirtableConnectorConfig , BaseConnector
from typing import Union ,Optional
import os
import requests
import pandas as pd

class AirtableConnector(BaseConnector):
    """
    Airtable connector to retrieving record data.
    """
    def __init__(
            self,
            baseid : Optional[str] = None,
            bearer_token : Optional[str] = None,
            table_name : Optional[str] = None,
            config : Union[AirtableConnectorConfig,dict] = None
    ):
        if not bearer_token and not config:
            raise ValueError(
                "You must specify bearer token for authentication or a config object."
            )
        if not baseid and not config.baseID:
            raise ValueError(
                "You must specify baseId or a proper config object."
            )
        if not isinstance(config,AirtableConnectorConfig):
            if not config :
                config = {}
            if table_name :
                config['table'] = table_name
            
            airtable_config = AirtableConnectorConfig(**config)
        else :
            airtable_config = config

        self._session = requests.Session()

        self._session.headers = {
            "Authorization" : f"Bearer {airtable_config['token']}"
        }

        self._response : str = None

        super().__init__(airtable_config)
    
    def _connect_load(self,config:AirtableConnectorConfig):
        """
        Authenticate and connect to the instance 

        Args :
            config (AirtableConnectorConfig) :Configuration to load table data.
        """
        _response = self._session.get(f"https://api.airtable.com/v0/{config['baseID']}/{config['table']}")
        if _response.status_code == 200 :
            self._response = pd.read_json(_response.json())
        else :
            raise ValueError(
                "Please verify authentication details , baseid or table_name are correct ."
            )
        
    
    def head(self):
        """
        Return the head of the table that the connector is connected to.

        Returns :
            DatFrameType: The head of the data source that the conector is connected to . 
        """
        return self._response.head()
        