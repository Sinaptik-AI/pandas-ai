"""
Base connector class to be extended by all connectors.
"""

from abc import ABC, abstractmethod
from ..helpers.df_info import DataFrameType
from ..helpers.logger import Logger
from pydantic import BaseModel
from typing import Optional


class ConnectorConfig(BaseModel):
    """
    Connector configuration.
    """

    dialect: Optional[str] = None
    driver: Optional[str] = None
    username: str
    password: str
    host: str
    port: int
    database: str
    table: str
    where: list[list[str]] = None


class BaseConnector(ABC):
    """
    Base connector class to be extended by all connectors.
    """

    _config = None
    _logger: Logger = None
    _additional_filters: list[list[str]] = None

    def __init__(self, config):
        """
        Initialize the connector with the given configuration.

        Args:
            config (dict): The configuration for the connector.
        """
        self._config = config

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
        return (
            self.__class__.__name__
            + "://"
            + self._config.host
            + ":"
            + str(self._config.port)
            + "/"
            + self._config.database
            + "/"
            + self._config.table
        )

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
