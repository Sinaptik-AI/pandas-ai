"""
Base connector class to be extended by all connectors.
"""

import json
import os
from abc import ABC, abstractmethod
from functools import cache
from typing import Union

import pandasai.pandas as pd
from pandasai.helpers.dataframe_serializer import (
    DataframeSerializer,
    DataframeSerializerType,
)
from pandasai.pydantic import BaseModel

from ..helpers.logger import Logger


class BaseConnectorConfig(BaseModel):
    """
    Base Connector configuration.
    """

    database: str
    table: str
    where: list[list[str]] = None


class BaseConnector(ABC):
    """
    Base connector class to be extended by all connectors.
    """

    _logger: Logger = None
    _additional_filters: list[list[str]] = None

    def __init__(
        self,
        config: Union[BaseConnectorConfig, dict],
        name: str = None,
        description: str = None,
        custom_head: pd.DataFrame = None,
        field_descriptions: dict = None,
    ):
        """
        Initialize the connector with the given configuration.

        Args:
            config (dict): The configuration for the connector.
        """
        if isinstance(config, dict):
            config = self._load_connector_config(config)

        self.config = config
        self.name = name
        self.description = description
        self.custom_head = custom_head
        self.field_descriptions = field_descriptions

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
    def head(self, n: int = 3) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the
        data source.
        """
        pass

    @abstractmethod
    def execute(self) -> pd.DataFrame:
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
        self._additional_filters = filters or []

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
        path = f"{self.__class__.__name__}://{self.config.host}:"
        if hasattr(self.config, "port"):
            path += str(self.config.port)
        path += f"/{self.config.database}/{self.config.table}"
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

    @property
    def pandas_df(self):
        """
        Returns the pandas dataframe
        """
        raise NotImplementedError

    def equals(self, other):
        return self.__dict__ == other.__dict__

    @cache
    def get_head(self, n: int = 3) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the
        data source.

        Args:
            n (int, optional): The number of rows to return. Defaults to 5.

        Returns:
            pd.DataFrame: The head of the data source that the connector is
                connected to.
        """
        return self.custom_head if self.custom_head is not None else self.head(n)

    def head_with_truncate_columns(self, max_size=25) -> pd.DataFrame:
        """
        Truncate the columns of the dataframe to a maximum of 20 characters.

        Args:
            df (pd.DataFrame): The dataframe to truncate the columns of.

        Returns:
            pd.DataFrame: The dataframe with truncated columns.
        """
        df_trunc = self.get_head().copy()

        for col in df_trunc.columns:
            if df_trunc[col].dtype == "object":
                first_val = df_trunc[col].iloc[0]
                if isinstance(first_val, str) and len(first_val) > max_size:
                    df_trunc[col] = f"{df_trunc[col].str.slice(0, max_size - 3)}..."

        return df_trunc

    @cache
    def get_schema(self) -> pd.DataFrame:
        """
        A sample of the dataframe.

        Returns:
            pd.DataFrame: A sample of the dataframe.
        """
        if self.get_head() is None:
            return None

        if len(self.get_head()) > 0:
            return self.head_with_truncate_columns()

        return self.get_head()

    @cache
    def to_csv(self) -> str:
        """
        A proxy-call to the dataframe's `.to_csv()`.

        Returns:
            str: The dataframe as a CSV string.
        """
        return self.get_head().to_csv(index=False)

    @cache
    def to_string(
        self,
        index: int = 0,
        is_direct_sql: bool = False,
        serializer: DataframeSerializerType = None,
    ) -> str:
        """
        Convert dataframe to string
        Returns:
            str: dataframe string
        """
        return DataframeSerializer().serialize(
            self,
            extras={
                "index": index,
                "type": "sql" if is_direct_sql else "pd.DataFrame",
                "is_direct_sql": is_direct_sql,
            },
            type_=serializer,
        )

    @cache
    def to_json(self):
        df_head = self.get_head()

        return {
            "name": self.name,
            "description": self.description,
            "head": json.loads(df_head.to_json(orient="records", date_format="iso")),
        }
