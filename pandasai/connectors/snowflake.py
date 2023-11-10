"""
SnowFlake connectors are used to connect to SnowFlake Data Cloud.
"""

import pandas as pd
from .base import BaseConnectorConfig, SnowFlakeConnectorConfig
from sqlalchemy import create_engine
from functools import cache
from typing import Union
from .sql import SQLConnector


class SnowFlakeConnector(SQLConnector):
    """
    SnowFlake connectors are used to connect to SnowFlake Data Cloud.
    """

    def __init__(self, config: Union[SnowFlakeConnectorConfig, dict]):
        """
        Initialize the SnowFlake connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the SnowFlake connector.
        """
        config["dialect"] = "snowflake"

        if isinstance(config, dict):
            snowflake_env_vars = {
                "account": "SNOWFLAKE_HOST",
                "database": "SNOWFLAKE_DATABASE",
                "warehouse": "SNOWFLAKE_WAREHOUSE",
                "dbSchema": "SNOWFLAKE_SCHEMA",
                "username": "SNOWFLAKE_USERNAME",
                "password": "SNOWFLAKE_PASSWORD",
            }
            config = self._populate_config_from_env(config, snowflake_env_vars)

        super().__init__(config)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return SnowFlakeConnectorConfig(**config)

    def _init_connection(self, config: SnowFlakeConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (SQLConnectorConfig): Configurations to load database

        """
        self._engine = create_engine(
            f"{config.dialect}://{config.username}:{config.password}@{config.account}/?warehouse={config.warehouse}&database={config.database}&schema={config.dbSchema}"
        )

        self._connection = self._engine.connect()

    @cache
    def head(self):
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.
        """

        if self.logger:
            self.logger.log(
                f"Getting head of {self._config.table} "
                f"using dialect {self._config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=5, order="RANDOM()")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)

    def __repr__(self):
        """
        Return the string representation of the SnowFlake connector.

        Returns:
            str: The string representation of the SnowFlake connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self._config.dialect} "
            f"Account={self._config.account} "
            f"warehouse={self._config.warehouse} "
            f"database={self._config.database} schema={str(self._config.dbSchema)}  "
            f"table={self._config.table}>"
        )

    def equals(self, other):
        if isinstance(other, self.__class__):
            return (
                self._config.dialect,
                self._config.account,
                self._config.username,
                self._config.password,
            ) == (
                other._config.dialect,
                other._config.account,
                other._config.username,
                other._config.password,
            )
        return False
