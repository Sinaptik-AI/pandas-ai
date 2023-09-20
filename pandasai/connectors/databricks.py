"""
Databricks Connector to connects you to your Databricks SQL Warhouse on
Azure, AWS and GCP
"""

import os
from .base import BaseConnectorConfig, DatabricksConnectorConfig
from sqlalchemy import create_engine
from typing import Union
from .sql import SQLConnector


class DatabricksConnector(SQLConnector):
    """
    SnowFlake connectors are used to connect to SnowFlake Data Cloud.
    """

    def __init__(self, config: DatabricksConnectorConfig):
        """
        Initialize the SnowFlake connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the SnowFlake connector.
        """
        config["dialect"] = "databricks"

        if "token" not in config and os.getenv("DATABRICKS_TOKEN"):
            config["token"] = os.getenv("DATABRICKS_TOKEN")
        if "database" not in config and os.getenv("SNOWFLAKE_DATABASE"):
            config["database"] = os.getenv("SNOWFLAKE_DATABASE")
        if "host" not in config and os.getenv("DATABRICKS_HOST"):
            config["host"] = os.getenv("DATABRICKS_HOST")
        if "port" not in config and os.getenv("DATABRICKS_PORT"):
            config["port"] = os.getenv("DATABRICKS_PORT")
        if "httpPath" not in config and os.getenv("DATABRICKS_HTTP_PATH"):
            config["httpPath"] = os.getenv("DATABRICKS_HTTP_PATH")

        super().__init__(config)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return DatabricksConnectorConfig(**config)

    def _init_connection(self, config: DatabricksConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (SQLConnectorConfig): Configurations to load database

        """
        self._engine = create_engine(
            f"{config.dialect}://token:{config.token}@{config.host}:{config.port}?http_path={config.httpPath}"
        )

        self._connection = self._engine.connect()

    def __repr__(self):
        """
        Return the string representation of the SnowFlake connector.

        Returns:
        str: The string representation of the SnowFlake connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self._config.dialect} "
            f"token={self._config.token} "
            f"host={self._config.host} port={self._config.port} "
            f"database={self._config.database} httpPath={str(self._config.httpPath)}"
        )
