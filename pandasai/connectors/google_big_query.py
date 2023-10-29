"""
Google Big Query connector is used to connect to dataset from
google big query api.
"""

from sqlalchemy import create_engine
from .base import GoogleBigQueryConnectorConfig
from .base import BaseConnectorConfig
from .sql import SQLConnector
from typing import Union


class GoogleBigQueryConnector(SQLConnector):
    """
    GoogleBigQuery Connectors are used to connect to BigQuery Data Cloud.
    """

    def __init__(self, config: Union[GoogleBigQueryConnectorConfig, dict]):
        """
        Initialize the GoogleBigQuery connector with the given configuration.

        Args:
            config (ConnectorConfig): The config for the GoogleBigQuery connector.
        """
        config["dialect"] = "bigquery"
        if isinstance(config, dict):
            env_vars = {
                "database": "BIG_QUERY_DATABASE",
                "credentials_path": "KEYFILE_PATH",
                "projectID": "PROJECT_ID",
            }
            config = self._populate_config_from_env(config, env_vars)

        super().__init__(config)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return GoogleBigQueryConnectorConfig(**config)

    def _init_connection(self, config: GoogleBigQueryConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (GoogleBigQueryConnectorConfig): Configurations to load database

        """

        self._engine = create_engine(
            f"{config.dialect}://{config.projectID}/{config.database}",
            credentials_path=config.credentials_path,
        )

        self._connection = self._engine.connect()

    def __repr__(self):
        """
        Return the string representation of the Google big query connector.

        Returns:
        str: The string representation of the Google big query connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self._config.dialect} "
            f"projectid= {self._config.projectID} database={self._config.database} >"
        )
