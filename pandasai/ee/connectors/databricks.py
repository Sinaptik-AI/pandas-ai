"""
Databricks Connector to connects you to your Databricks SQL Warhouse on
Azure, AWS and GCP
"""

from typing import Union

from sqlalchemy import create_engine

from ...connectors.base import BaseConnectorConfig
from ...connectors.sql import SQLBaseConnectorConfig, SQLConnector


class DatabricksConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration for DataBricks.
    """

    host: str
    port: int
    token: str
    httpPath: str


class DatabricksConnector(SQLConnector):
    """
    Databricks connectors are used to connect to Databricks Data Cloud.
    """

    def __init__(
        self,
        config: Union[DatabricksConnectorConfig, dict],
        **kwargs,
    ):
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

        super().__init__(config, **kwargs)

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
            f"<{self.__class__.__name__} dialect={self.config.dialect} "
            f"host={self.config.host} port={self.config.port} "
            f"database={self.config.database} httpPath={str(self.config.httpPath)}"
        )

    def equals(self, other):
        if isinstance(other, self.__class__):
            return (
                self.config.dialect,
                self.config.host,
                self.config.port,
                self.config.httpPath,
            ) == (
                other.config.dialect,
                other.config.host,
                other.config.port,
                other.config.httpPath,
            )
        return False
