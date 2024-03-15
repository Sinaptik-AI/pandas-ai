"""
Pandas connector class to handle csv, parquet, xlsx files and pandas dataframes.
"""

import hashlib
from functools import cache, cached_property
from typing import Union

from pydantic import BaseModel

import pandasai.pandas as pd

from ..helpers.data_sampler import DataSampler
from ..helpers.file_importer import FileImporter
from ..helpers.logger import Logger
from .base import BaseConnector


class PandasConnectorConfig(BaseModel):
    """
    Pandas Connector configuration.
    """

    original_df: Union[pd.DataFrame, pd.Series, str, list, dict]

    class Config:
        arbitrary_types_allowed = True


class PandasConnector(BaseConnector):
    """
    Pandas connector class to handle csv, parquet, xlsx files and pandas dataframes.
    """

    pandas_df = pd.DataFrame
    _logger: Logger = None
    _additional_filters: list[list[str]] = None

    def __init__(
        self,
        config: Union[PandasConnectorConfig, dict],
        **kwargs,
    ):
        """
        Initialize the Pandas connector with the given configuration.

        Args:
            config (PandasConnectorConfig): The configuration for the Pandas connector.
        """
        super().__init__(config, **kwargs)

        self._load_df(self.config.original_df)

    def _load_df(self, df: Union[pd.DataFrame, pd.Series, str, list, dict]):
        """
        Load the dataframe from a file or pandas dataframe.

        Args:
            df (Union[pd.DataFrame, pd.Series, str, list, dict]): The dataframe to load.
        """
        if isinstance(df, pd.Series):
            self.pandas_df = df.to_frame()
        elif isinstance(df, pd.DataFrame):
            self.pandas_df = df
        elif isinstance(df, (list, dict)):
            try:
                self.pandas_df = pd.DataFrame(df)
            except Exception as e:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                ) from e
        elif isinstance(df, str):
            self.pandas_df = FileImporter.import_from_file(df)
        else:
            raise ValueError("Invalid input data. We cannot convert it to a dataframe.")

    def _load_connector_config(
        self, config: Union[PandasConnectorConfig, dict]
    ) -> PandasConnectorConfig:
        """
        Loads passed Configuration to object

        Args:
            config (PandasConnectorConfig): Construct config in structure

            Returns:
                config: PandasConnectorConfig
        """
        return PandasConnectorConfig(**config)

    @cache
    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the
        data source.
        """
        sampler = DataSampler(self.pandas_df)
        return sampler.sample(n)

    @cache
    def execute(self) -> pd.DataFrame:
        """
        Execute the given query on the data source that the connector is
        connected to.
        """
        return self.pandas_df

    @cached_property
    def rows_count(self):
        """
        Return the number of rows in the data source that the connector is
        connected to.
        """
        return len(self.pandas_df)

    @cached_property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.
        """
        return len(self.pandas_df.columns)

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.
        """
        columns_str = "".join(self.pandas_df.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    @cached_property
    def path(self):
        """
        Return the path of the data source that the connector is connected to.
        """
        pass

    @property
    def fallback_name(self):
        """
        Return the name of the table that the connector is connected to.
        """
        pass

    def equals(self, other: BaseConnector):
        """
        Return whether the data source that the connector is connected to is
        equal to the other data source.
        """
        return self._original_df.equals(other._original_df)
