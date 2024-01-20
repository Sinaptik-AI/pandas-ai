"""
Databricks Connector to connects you to your Databricks SQL Warhouse on
Azure, AWS and GCP
"""

from typing import Union

from sqlalchemy import create_engine

from .base import BaseConnectorConfig, DatabricksConnectorConfig
from .sql import SQLConnector


class DatabricksConnector(SQLConnector):
    """
    Databricks connectors are used to connect to Databricks Data Cloud.
    """

    def __init__(self, config: Union[DatabricksConnectorConfig, dict]):
        """
        Initialize the Databricks connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the Databricks connector.
        """
        config["dialect"] = "databricks"
        if isinstance(config, dict):
            env_vars = {
                "token": "DATABRICKS_TOKEN",
                "database": "DATABRICKS_DATABASE",
                "host": "DATABRICKS_HOST",
                "port": "DATABRICKS_PORT",
                "httpPath": "DATABRICKS_HTTP_PATH",
            }
            config = self._populate_config_from_env(config, env_vars)

        super().__init__(config)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return DatabricksConnectorConfig(**config)

    def _init_connection(self, config: DatabricksConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (DatabricksConnectorConfig): Configurations to load database

        """
        self._engine = create_engine(
            f"{config.dialect}://token:{config.token}@{config.host}:{config.port}?http_path={config.httpPath}"
        )

        self._connection = self._engine.connect()

    def __repr__(self):
        """
        Return the string representation of the Databricks connector.

        Returns:
        str: The string representation of the Databricks connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self._config.dialect} "
            f"host={self._config.host} port={self._config.port} "
            f"database={self._config.database} httpPath={str(self._config.httpPath)}"
        )

    def equals(self, other):
        if isinstance(other, self.__class__):
            return (
                self._config.dialect,
                self._config.token,
                self._config.host,
                self._config.port,
                self._config.httpPath,
            ) == (
                other._config.dialect,
                other._config.token,
                other._config.host,
                other._config.port,
                other._config.httpPath,
            )
        return False
