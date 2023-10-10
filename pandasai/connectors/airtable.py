"""
Airtable connectors are used to connect airtable records.
"""

from .base import AirtableConnectorConfig, BaseConnector, BaseConnectorConfig
from typing import Union, Optional
import requests
import pandas as pd


class AirtableConnector(BaseConnector):
    """
    Airtable connector to retrieving record data.
    """

    def __init__(
        self,
        config: Optional[Union[AirtableConnectorConfig, dict]] = None,
    ):
        if isinstance(config, dict):
            if config["token"] and config["baseID"] and config["table"]:
                config = AirtableConnectorConfig(**config)

        elif not config:
            airtable_env_vars = {
                "token": "AIRTABLE_AUTH_TOKEN",
                "baseID": "AIRTABLE_BASE_ID",
                "table": "AIRTABLE_TABLE_NAME",
            }
            config = AirtableConnectorConfig(
                **self._populate_config_from_env(config, airtable_env_vars)
            )

        self._root_url: str = "https://api.airtable.com/v0/"

        super().__init__(config)

    def _init_connection(self, config: BaseConnectorConfig):
        """
        make connection to database
        """
        config = config.dict()
        _session = requests.Session()
        _session.headers = {"Authorization": f"Bearer {config['token']}"}
        url = f"{self._root_url}{config['baseID']}/{config['table']}"
        response = _session.head(url=url)
        if response.status_code == 200:
            self._session = _session
        else:
            raise ValueError(
                f"""Failed to connect to Airtable. 
                Status code: {response.status_code}, 
                message: {response.text}"""
            )

    def execute(self):
        """
        Execute the connector and return the result.

        Returns:
            DataFrameType: The result of the connector.
        """
        url = f"{self._root_url}{self.config['baseID']}/{self.config['table']}"
        if self._session:
            _response = self._session.get(url)
            if _response.status_code == 200:
                data = _response.json()
                ## Following column selection is done
                ## to prepare output in favaourable format.
                records = [
                    {"id": record["id"], **record["fields"]}
                    for record in data["records"]
                ]
                self._response = pd.DataFrame(records)
            else:
                raise ValueError(
                    f"""Failed to connect to Airtable. 
                    Status code: {_response.status_code}, 
                    message: {_response.text}"""
                )
        return self._response

    def head(self):
        """
        Return the head of the table that
          the connector is connected to.

        Returns :
            DatFrameType: The head of the data source
                 that the conector is connected to .
        """
        return self._response.head()
