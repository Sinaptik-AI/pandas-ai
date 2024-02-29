"""
SnowFlake connectors are used to connect to SnowFlake Data Cloud.
"""

from functools import cache
from typing import Union

from sqlalchemy import create_engine

import pandasai.pandas as pd

from ...connectors.base import BaseConnectorConfig
from ...connectors.sql import SQLBaseConnectorConfig, SQLConnector


class SnowFlakeConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration for SnowFlake.
    """

    account: str
    database: str
    username: str
    password: str
    dbSchema: str
    warehouse: str


class SnowFlakeConnector(SQLConnector):
    """
    SnowFlake connectors are used to connect to SnowFlake Data Cloud.
    """

    def __init__(
        self,
        config: Union[SnowFlakeConnectorConfig, dict],
        **kwargs,
    ):
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

        super().__init__(config, **kwargs)

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
    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.
        """

        if self.logger:
            self.logger.log(
                f"Getting head of {self.config.table} "
                f"using dialect {self.config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=n, order="RANDOM()")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)

    def __repr__(self):
        """
        Return the string representation of the SnowFlake connector.

        Returns:
            str: The string representation of the SnowFlake connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self.config.dialect} "
            f"Account={self.config.account} "
            f"warehouse={self.config.warehouse} "
            f"database={self.config.database} schema={str(self.config.dbSchema)}  "
            f"table={self.config.table}>"
        )

    def equals(self, other):
        if isinstance(other, self.__class__):
            return (
                self.config.dialect,
                self.config.dbSchema,
                self.config.warehouse,
                self.config.account,
            ) == (
                other.config.dialect,
                other.config.dbSchema,
                other.config.warehouse,
                other.config.account,
            )
        return False
