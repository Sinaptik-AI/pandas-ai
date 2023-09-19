"""
SnowFlake connectors are used to connect to SnowFlake Data Cloud.
"""

import os
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

    def __init__(self, config: SnowFlakeConnectorConfig):
        """
        Initialize the SnowFlake connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the SnowFlake connector.
        """
        config["dialect"] = "snowflake"

        if "account" not in config and os.getenv("SNOWFLAKE_HOST"):
            config["account"] = os.getenv("SNOWFLAKE_HOST")
        if "database" not in config and os.getenv("SNOWFLAKE_DATABASE"):
            config["database"] = os.getenv("SNOWFLAKE_DATABASE")
        if "warehouse" not in config and os.getenv("SNOWFLAKE_WAREHOUSE"):
            config["warehouse"] = os.getenv("SNOWFLAKE_WAREHOUSE")
        if "dbSchema" not in config and os.getenv("SNOWFLAKE_SCHEMA"):
            config["dbSchema"] = os.getenv("SNOWFLAKE_SCHEMA")
        if "username" not in config and os.getenv("SNOWFLAKE_USERNAME"):
            config["username"] = os.getenv("SNOWFLAKE_USERNAME")
        if "password" not in config and os.getenv("SNOWFLAKE_PASSWORD"):
            config["password"] = os.getenv("SNOWFLAKE_PASSWORD")

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
            f"username={self._config.username} "
            f"password={self._config.password} Account={self._config.account} "
            f"warehouse={self._config.warehouse} "
            f"database={self._config.database} schema={str(self._config.dbSchema)}  "
            f"table={self._config.table}>"
        )
