"""
Polars connector class to handle csv, parquet, xlsx files and polars dataframes.
"""

from functools import cache, cached_property
from typing import TYPE_CHECKING, Any, Union

import pandasai.pandas as pd

# Use a conditional import for type checking
if TYPE_CHECKING:
    try:
        import polars as pl

        PolarsDataFrame = pl.DataFrame
        PolarsSeries = pl.Series
    except ImportError:
        PolarsDataFrame = Any
        PolarsSeries = Any
else:
    PolarsDataFrame = Any
    PolarsSeries = Any

from pydantic import BaseModel

from ..helpers.data_sampler import DataSampler
from ..helpers.file_importer import FileImporter
from ..helpers.logger import Logger
from .base import BaseConnector


class PolarsConnectorConfig(BaseModel):
    """
    Polars Connector configuration.
    """

    original_df: PolarsDataFrame

    class Config:
        arbitrary_types_allowed = True


class PolarsConnector(BaseConnector):
    """
    Polars connector class to handle csv, parquet, xlsx files and polars dataframes.
    """

    pandas_df = pd.DataFrame
    _logger: Logger = None
    _additional_filters: list[list[str]] = None

    def __init__(
        self,
        config: Union[PolarsConnectorConfig, dict],
        **kwargs,
    ):
        """
        Initialize the Polars connector with the given configuration.

        Args:
            config (PolarsConnectorConfig): The configuration for the Polars connector.
        """

        super().__init__(config, **kwargs)

        self._load_df(self.config.original_df)

    def _load_df(self, df: Union[PolarsDataFrame, PolarsSeries, str, dict]):
        """
        Load the dataframe from a file or polars dataframe.

        Args:
            df (Union[pl.DataFrame, pl.Series, str, dict]): The dataframe to load.
        """
        polars_df = None
        if isinstance(df, pl.Series):
            polars_df = df.to_frame()
        elif isinstance(df, pl.DataFrame):
            polars_df = df
        elif isinstance(df, str):
            polars_df = FileImporter.import_from_file(df)
        elif isinstance(df, dict):
            try:
                polars_df = pl.DataFrame(df)
            except Exception as e:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                ) from e
        else:
            raise ValueError("Invalid input data. We cannot convert it to a dataframe.")

        self.pandas_df = polars_df.to_pandas()

    def _load_connector_config(
        self, config: Union[PolarsConnectorConfig, dict]
    ) -> PolarsConnectorConfig:
        """
        Loads passed Configuration to object

        Args:
            config (PolarsConnectorConfig): Construct config in structure

            Returns:
                config: PolarsConnectorConfig
        """
        return PolarsConnectorConfig(**config)

    @cache
    def head(self, n: int = 5) -> PolarsDataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the
        data source.
        """
        if self.pandas_df is None:
            return None

        sampler = DataSampler(self.pandas_df)
        return sampler.sample(n)

    @cache
    def execute(self) -> PolarsDataFrame:
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
        return len(self.pandas_df) if self.pandas_df.index else 0

    @cached_property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.
        """
        return len(self.pandas_df.columns) if self.pandas_df.columns else 0

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.
        """
        import hashlib

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
