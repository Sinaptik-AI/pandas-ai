"""
Google Big Query connector is used to connect to dataset from
google big query api.
"""

from typing import Union

from sqlalchemy import create_engine

from pandasai.exceptions import InvalidConfigError

from ...connectors.base import BaseConnectorConfig
from ...connectors.sql import SQLBaseConnectorConfig, SQLConnector


class GoogleBigQueryConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration for big query.
    """

    credentials_path: str = None
    credentials_base64: str = None
    database: str
    table: str
    projectID: str


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

        if "credentials_base64" not in config and "credentials_path" not in config:
            raise InvalidConfigError(
                "credentials_path or credentials_base64 is needed to connect"
            )

        super().__init__(config)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return GoogleBigQueryConnectorConfig(**config)

    def _init_connection(self, config: GoogleBigQueryConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (GoogleBigQueryConnectorConfig): Configurations to load database

        """
        if config.credentials_path:
            self._engine = create_engine(
                f"{config.dialect}://{config.projectID}/{config.database}",
                credentials_path=config.credentials_path,
            )
        else:
            self._engine = create_engine(
                f"{config.dialect}://{config.projectID}/{config.database}?credentials_base64={config.credentials_base64}"
            )

        self._connection = self._engine.connect()

    def __repr__(self):
        """
        Return the string representation of the Google big query connector.

        Returns:
        str: The string representation of the Google big query connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self.config.dialect} "
            f"projectid= {self.config.projectID} database={self.config.database} >"
        )
