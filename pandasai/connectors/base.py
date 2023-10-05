"""
Base connector class to be extended by all connectors.
"""

from abc import ABC, abstractmethod
import os
from ..helpers.df_info import DataFrameType
from ..helpers.logger import Logger
from pydantic import BaseModel
from typing import Optional, Union


class BaseConnectorConfig(BaseModel):
    """
    Base Connector configuration.
    """

    database: str
    table: str
    where: list[list[str]] = None


class SQLBaseConnectorConfig(BaseConnectorConfig):
    """
    Base Connector configuration.
    """

    driver: Optional[str] = None
    dialect: Optional[str] = None


class YahooFinanceConnectorConfig(BaseConnectorConfig):
    """
    Connector configuration for Yahoo Finance.
    """

    dialect: str = "yahoo_finance"
    host: str = "yahoo.finance.com"
    database: str = "stock_data"
    host: str


class SQLConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration.
    """

    host: str
    port: int
    username: str
    password: str


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


class DatabricksConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration for DataBricks.
    """

    host: str
    port: int
    token: str
    httpPath: str


class BaseConnector(ABC):
    """
    Base connector class to be extended by all connectors.
    """

    _config: BaseConnectorConfig = None
    _logger: Logger = None
    _additional_filters: list[list[str]] = None

    def __init__(self, config: Union[BaseConnectorConfig, dict]):
        """
        Initialize the connector with the given configuration.

        Args:
            config (dict): The configuration for the connector.
        """
        if isinstance(config, dict):
            config = self._load_connector_config(config)

        self._config = config

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        """Loads passed Configuration to object

        Args:
            config (BaseConnectorConfig): Construct config in structure

        Returns:
            config: BaseConnectorConfig
        """
        pass

    def _populate_config_from_env(self, config: dict, envs_mapping: dict):
        """
        Populate the configuration dictionary with values from environment variables
        if not exists in the config.

        Args:
            config (dict): The configuration dictionary to be populated.
            envs_mapping (dict): The dictionary representing a map of config's keys
                and according names of the environment variables.

        Returns:
            dict: The populated configuration dictionary.
        """

        for key, env_var in envs_mapping.items():
            if key not in config and os.getenv(env_var):
                config[key] = os.getenv(env_var)

        return config

    def _init_connection(self, config: BaseConnectorConfig):
        """
        make connection to database
        """
        pass

    @abstractmethod
    def head(self):
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the
        data source.
        """
        pass

    @abstractmethod
    def execute(self) -> DataFrameType:
        """
        Execute the given query on the data source that the connector is
        connected to.
        """
        pass

    def set_additional_filters(self, filters: dict):
        """
        Add additional filters to the connector.

        Args:
            filters (dict): The additional filters to add to the connector.
        """
        self._additional_filters = filters if filters else []

    @property
    def rows_count(self):
        """
        Return the number of rows in the data source that the connector is
        connected to.
        """
        raise NotImplementedError

    @property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.
        """
        raise NotImplementedError

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.
        """
        raise NotImplementedError

    @property
    def path(self):
        """
        Return the path of the data source that the connector is connected to.
        """
        # JDBC string
        path = self.__class__.__name__ + "://" + self._config.host + ":"
        if hasattr(self._config, "port"):
            path += str(self._config.port)
        path += "/" + self._config.database + "/" + self._config.table
        return path

    @property
    def logger(self):
        """
        Return the logger for the connector.
        """
        return self._logger

    @logger.setter
    def logger(self, logger: Logger):
        """
        Set the logger for the connector.

        Args:
            logger (Logger): The logger for the connector.
        """
        self._logger = logger

    @property
    def fallback_name(self):
        """
        Return the name of the table that the connector is connected to.
        """
        raise NotImplementedError
