"""
A smart dataframe class is a wrapper around the pandas/polars dataframe that allows you
to query it using natural language. It uses the LLMs to generate Python code from
natural language and then executes it on the dataframe.

Example:
    ```python
    from pandasai.smart_dataframe import SmartDataframe
    from pandasai.llm.openai import OpenAI
    
    df = pd.read_csv("examples/data/Loan payments data.csv")
    llm = OpenAI()
    
    df = SmartDataframe(df, config={"llm": llm})
    response = df.chat("What is the average loan amount?")
    print(response)
    # The average loan amount is $15,000.
    ```
"""

import hashlib

import pandas as pd
from functools import cached_property
from ..smart_datalake import SmartDatalake
from ..helpers.df_config import Config
from ..helpers.data_sampler import DataSampler

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.from_google_sheets import from_google_sheets
from typing import List, Union
from ..middlewares.base import Middleware
from ..helpers.df_info import DataFrameType, df_type
from .abstract_df import DataframeAbstract
from ..callbacks.base import BaseCallback
from ..llm import LLM, LangchainLLM
from ..connectors.base import BaseConnector


class SmartDataframeCore:
    """
    A smart dataframe class is a wrapper around the pandas/polars dataframe that allows
    you to query it using natural language. It uses the LLMs to generate Python code
    from natural language and then executes it on the dataframe.
    """

    _df = None
    _df_loaded: bool = True
    _connector: BaseConnector = None
    _engine: str = None

    def __init__(self, df: DataFrameType):
        self._load_dataframe(df)

    def _load_dataframe(self, df):
        """
        Load the dataframe from a file or a connector.

        Args:
            df (Union[pd.DataFrame, pl.DataFrame, BaseConnector]):
            Pandas or Polars dataframe or a connector.
        """

        if isinstance(df, BaseConnector):
            self._df = None
            self.connector = df
            self._df_loaded = False
        else:
            self.dataframe = df

    def _import_from_file(self, file_path: str):
        """
        Import a dataframe from a file (csv, parquet, xlsx)

        Args:
            file_path (str): Path to the file to be imported.

        Returns:
            pd.DataFrame: Pandas dataframe
        """

        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".parquet"):
            return pd.read_parquet(file_path)
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        elif file_path.startswith("https://docs.google.com/spreadsheets/"):
            return from_google_sheets(file_path)[0]
        else:
            raise ValueError("Invalid file format.")

    def _load_engine(self):
        engine = df_type(self.dataframe)

        if engine is None:
            raise ValueError(
                "Invalid input data. Must be a Pandas or Polars dataframe."
            )

        self._engine = engine

    def _validate_and_convert_dataframe(self, df: DataFrameType) -> DataFrameType:
        if isinstance(df, str):
            return self._import_from_file(df)
        elif isinstance(df, (list, dict)):
            # if the list or dictionary can be converted to a dataframe, convert it
            # otherwise, raise an error
            try:
                return pd.DataFrame(df)
            except ValueError:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                )
        else:
            return df

    @property
    def dataframe(self) -> DataFrameType:
        if self._df_loaded:
            return self._df
        elif self.connector:
            self._df = self.connector.execute()
            self._df_loaded = True
            return self._df

    @dataframe.setter
    def dataframe(self, df: DataFrameType):
        """
        Load a dataframe into the smart dataframe

        Args:
            df (DataFrameType): Pandas or Polars dataframe or path to a file
        """
        df = self._validate_and_convert_dataframe(df)
        self._df = df

        if df is not None:
            self._load_engine()

    @property
    def engine(self) -> str:
        return self._engine

    @property
    def connector(self):
        return self._connector

    @connector.setter
    def connector(self, connector: BaseConnector):
        self._connector = connector


class SmartDataframe(DataframeAbstract, Shortcuts):
    _table_name: str
    _table_description: str
    _core: SmartDataframeCore
    _lake: SmartDatalake

    def __init__(
        self,
        df: DataFrameType,
        name: str = None,
        description: str = None,
        config: Config = None,
        logger: Logger = None,
    ):
        """
        Args:
            df (Union[pd.DataFrame, pl.DataFrame]): Pandas or Polars dataframe
            name (str, optional): Name of the dataframe. Defaults to None.
            description (str, optional): Description of the dataframe. Defaults to "".
            config (Config, optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """
        self._table_name = name
        self._table_description = description
        self._core = SmartDataframeCore(df)
        self._lake = SmartDatalake([self], config, logger)

        # If no name is provided, use the fallback name provided the connector
        if self._table_name is None and self.connector:
            self._table_name = self.connector.fallback_name

    def add_middlewares(self, *middlewares: List[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: A list of middlewares

        """
        self.lake.add_middlewares(*middlewares)

    def chat(self, query: str):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe

        Raises:
            ValueError: If the query is empty
        """
        return self.lake.chat(query)

    def column_hash(self) -> str:
        """
        Get the hash of the columns of the dataframe.

        Returns:
            str: Hash of the columns of the dataframe
        """
        if not self._df_loaded and self.connector:
            return self.connector.column_hash

        columns_str = "".join(self.dataframe.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    @property
    def dataframe(self) -> DataFrameType:
        return self._core.dataframe

    @property
    def engine(self):
        return self._core.engine

    @property
    def connector(self):
        return self._core.connector

    @connector.setter
    def connector(self, connector: BaseConnector):
        connector.logger = self.logger
        self._core.connector = connector

    @property
    def lake(self) -> SmartDatalake:
        return self._lake

    @lake.setter
    def lake(self, lake: SmartDatalake):
        self._lake = lake

    @property
    def rows_count(self):
        if self._df_loaded:
            return self.dataframe.shape[0]
        elif self.connector is not None:
            return self.connector.rows_count
        else:
            raise ValueError(
                "Cannot determine rows_count. No dataframe or connector loaded."
            )

    @property
    def columns_count(self):
        if self._df_loaded:
            return self.dataframe.shape[1]
        elif self.connector is not None:
            return self.connector.columns_count
        else:
            raise ValueError(
                "Cannot determine columns_count. No dataframe or connector loaded."
            )

    def _get_sample_head(self) -> DataFrameType:
        head = None
        rows_to_display = 0 if self.lake.config.enforce_privacy else 5
        if not self._core._df_loaded and self.connector:
            head = self.connector.head()
        else:
            head = self.dataframe.head(rows_to_display)

        sampler = DataSampler(head)
        return sampler.sample(rows_to_display)

    @cached_property
    def head_csv(self):
        """
        Get the head of the dataframe as a CSV string.

        Returns:
            str: CSV string
        """
        df_head = self._get_sample_head()
        return df_head.to_csv(index=False)

    @property
    def last_prompt(self):
        return self.lake.last_prompt

    @property
    def last_prompt_id(self) -> str:
        return self.lake.last_prompt_id

    @property
    def last_code_generated(self):
        return self.lake.last_code_executed

    @property
    def last_result(self):
        return self.lake.last_result

    @property
    def last_error(self):
        return self.lake.last_error

    @property
    def cache(self):
        return self.lake.cache

    @property
    def middlewares(self):
        return self.lake.middlewares

    @property
    def logger(self):
        return self.lake.logger

    @logger.setter
    def logger(self, logger: Logger):
        self.lake.logger = logger

    @property
    def logs(self):
        return self.lake.logs

    @property
    def verbose(self):
        return self.lake.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self.lake.verbose = verbose

    @property
    def callback(self):
        return self.lake.callback

    @callback.setter
    def callback(self, callback: BaseCallback):
        self.lake.callback = callback

    @property
    def enforce_privacy(self):
        return self.lake.enforce_privacy

    @enforce_privacy.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self.lake.enforce_privacy = enforce_privacy

    @property
    def use_error_correction_framework(self):
        return self.lake.use_error_correction_framework

    @use_error_correction_framework.setter
    def use_error_correction_framework(self, use_error_correction_framework: bool):
        self.lake.use_error_correction_framework = use_error_correction_framework

    @property
    def custom_prompts(self):
        return self.lake.custom_prompts

    @custom_prompts.setter
    def custom_prompts(self, custom_prompts: dict):
        self.lake.custom_prompts = custom_prompts

    @property
    def save_charts(self):
        return self.lake.save_charts

    @save_charts.setter
    def save_charts(self, save_charts: bool):
        self.lake.save_charts = save_charts

    @property
    def save_charts_path(self):
        return self.lake.save_charts_path

    @save_charts_path.setter
    def save_charts_path(self, save_charts_path: str):
        self.lake.save_charts_path = save_charts_path

    @property
    def custom_whitelisted_dependencies(self):
        return self.lake.custom_whitelisted_dependencies

    @custom_whitelisted_dependencies.setter
    def custom_whitelisted_dependencies(
        self, custom_whitelisted_dependencies: List[str]
    ):
        self.lake.custom_whitelisted_dependencies = custom_whitelisted_dependencies

    @property
    def max_retries(self):
        return self.lake.max_retries

    @max_retries.setter
    def max_retries(self, max_retries: int):
        self.lake.max_retries = max_retries

    @property
    def llm(self):
        return self.lake.llm

    @llm.setter
    def llm(self, llm: Union[LLM, LangchainLLM]):
        self.lake.llm = llm

    @property
    def table_name(self):
        return self._table_name

    @property
    def table_description(self):
        return self._table_description

    def __getattr__(self, name):
        if name in self._core.__dir__():
            return getattr(self._core, name)
        elif name in self.dataframe.__dir__():
            return getattr(self.dataframe, name)
        else:
            return self.__getattribute__(name)

    def __getitem__(self, key):
        return self.dataframe.__getitem__(key)

    def __setitem__(self, key, value):
        return self.dataframe.__setitem__(key, value)

    def __dir__(self):
        return dir(self._core) + dir(self.dataframe) + dir(self.__class__)

    def __repr__(self):
        return self.dataframe.__repr__()

    def __len__(self):
        return len(self.dataframe)
