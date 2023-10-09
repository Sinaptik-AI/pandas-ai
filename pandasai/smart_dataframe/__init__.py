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
from io import StringIO

import pandas as pd
from functools import cached_property
import pydantic

from pandasai.helpers.df_validator import DfValidator

from ..smart_datalake import SmartDatalake
from ..schemas.df_config import Config
from ..helpers.data_sampler import DataSampler

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.df_config_manager import DfConfigManager
from ..helpers.from_google_sheets import from_google_sheets
from typing import List, Union, Optional
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
    _temporary_loaded: bool = False
    _connector: BaseConnector = None
    _engine: str = None
    _logger: Logger = None

    def __init__(self, df: DataFrameType, logger: Logger = None):
        self._logger = logger
        self._load_dataframe(df)

    def _load_dataframe(self, df):
        """
        Load the dataframe from a file or a connector.

        Args:
            df (Union[pd.DataFrame, pl.DataFrame, BaseConnector]):
            Pandas or Polars dataframe or a connector.
        """
        if isinstance(df, BaseConnector):
            self.dataframe = None
            self.connector = df
            self.connector.logger = self._logger
            self._df_loaded = False
        elif isinstance(df, str):
            self.dataframe = self._import_from_file(df)
        elif isinstance(df, pd.Series):
            self.dataframe = df.to_frame()
        elif isinstance(df, (list, dict)):
            # if the list can be converted to a dataframe, convert it
            # otherwise, raise an error
            try:
                self.dataframe = pd.DataFrame(df)
            except ValueError:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                )
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
        """
        Load the engine of the dataframe (Pandas or Polars)
        """
        engine = df_type(self._df)

        if engine is None:
            raise ValueError(
                "Invalid input data. Must be a Pandas or Polars dataframe."
            )

        self._engine = engine

    def _validate_and_convert_dataframe(self, df: DataFrameType) -> DataFrameType:
        """
        Validate the dataframe and convert it to a Pandas or Polars dataframe.

        Args:
            df (DataFrameType): Pandas or Polars dataframe or path to a file

        Returns:
            DataFrameType: Pandas or Polars dataframe
        """
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

    def load_connector(self, temporary: bool = False):
        """
        Load a connector into the smart dataframe

        Args:
            temporary (bool): Whether the connector is for one time usage.
                If `True` passed, the connector will be unbound during
                the next call of `dataframe` providing that dataframe has
                been loaded.
        """
        self.dataframe = self.connector.execute()
        self._df_loaded = True
        self._temporary_loaded = temporary

    def _unload_connector(self):
        """
        Unload the connector from the smart dataframe.
        This is done when a partial dataframe is loaded from a connector (i.e.
        because of a filter) and we want to load the full dataframe or a different
        partial dataframe.
        """
        self._df = None
        self._df_loaded = False
        self._temporary_loaded = False

    @property
    def dataframe(self) -> DataFrameType:
        if self._df_loaded:
            return_df = None

            if self._engine == "polars":
                return_df = self._df.clone()
            elif self._engine == "pandas":
                return_df = self._df.copy()

            if self.has_connector and self._df_loaded and self._temporary_loaded:
                self._unload_connector()

            return return_df
        elif self.has_connector:
            return None

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

    @property
    def has_connector(self):
        return self._connector is not None


class SmartDataframe(DataframeAbstract, Shortcuts):
    _table_name: str
    _table_description: str
    _sample_head: str = None
    _original_import: any
    _core: SmartDataframeCore
    _lake: SmartDatalake

    def __init__(
        self,
        df: DataFrameType,
        name: str = None,
        description: str = None,
        sample_head: pd.DataFrame = None,
        config: Config = None,
        logger: Logger = None,
    ):
        """
        Args:
            df (Union[pd.DataFrame, pl.DataFrame]): Pandas or Polars dataframe
            name (str, optional): Name of the dataframe. Defaults to None.
            description (str, optional): Description of the dataframe. Defaults to "".
            sample_head (pd.DataFrame, optional): Sample head of the dataframe.
            config (Config, optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """
        self._original_import = df

        if isinstance(df, str):
            if not (
                df.endswith(".csv")
                or df.endswith(".parquet")
                or df.endswith(".xlsx")
                or df.startswith("https://docs.google.com/spreadsheets/")
            ):
                df_config = self._load_from_config(df)
                if df_config:
                    if "://" in df_config["import_path"]:
                        connector_name = df_config["import_path"].split("://")[0]
                        connector_path = df_config["import_path"].split("://")[1]
                        connector_host = connector_path.split(":")[0]
                        connector_port = connector_path.split(":")[1].split("/")[0]
                        connector_database = connector_path.split(":")[1].split("/")[1]
                        connector_table = connector_path.split(":")[1].split("/")[2]

                        connector_data = {
                            "host": connector_host,
                            "database": connector_database,
                            "table": connector_table,
                        }
                        if connector_port:
                            connector_data["port"] = connector_port

                        # instantiate the connector
                        df = getattr(
                            __import__(
                                "pandasai.connectors", fromlist=[connector_name]
                            ),
                            connector_name,
                        )(config=connector_data)
                    else:
                        df = df_config["import_path"]

                    if name is None:
                        name = df_config["name"]
                    if description is None:
                        description = df_config["description"]
                else:
                    raise ValueError(
                        "Could not find a saved dataframe configuration "
                        "with the given name."
                    )

        self._core = SmartDataframeCore(df, logger)

        self._table_name = name
        self._table_description = description
        self._lake = SmartDatalake([self], config, logger)

        # If no name is provided, use the fallback name provided the connector
        if self._table_name is None and self.connector:
            self._table_name = self.connector.fallback_name

        if sample_head is not None:
            self._sample_head = sample_head.to_csv(index=False)

    def add_middlewares(self, *middlewares: Optional[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: Middlewares to be added

        """
        self.lake.add_middlewares(*middlewares)

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe
            output_type (Optional[str]): Add a hint for LLM of which
                type should be returned by `analyze_data()` in generated
                code. Possible values: "number", "dataframe", "plot", "string":
                    * number - specifies that user expects to get a number
                        as a response object
                    * dataframe - specifies that user expects to get
                        pandas/polars dataframe as a response object
                    * plot - specifies that user expects LLM to build
                        a plot
                    * string - specifies that user expects to get text
                        as a response object

        Raises:
            ValueError: If the query is empty
        """
        return self.lake.chat(query, output_type)

    def column_hash(self) -> str:
        """
        Get the hash of the columns of the dataframe.

        Returns:
            str: Hash of the columns of the dataframe
        """
        if not self._core._df_loaded and self.connector:
            return self.connector.column_hash

        columns_str = "".join(self.dataframe.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    def save(self, name: str = None):
        """
        Saves the dataframe configuration to be used for later

        Args:
            name (str, optional): Name of the dataframe configuration. Defaults to None.
        """

        config_manager = DfConfigManager(self)
        config_manager.save(name)

    def load_connector(self, temporary: bool = False):
        """
        Load a connector into the smart dataframe

        Args:
            temporary (bool, optional): Whether the connector is temporary or not.
            Defaults to False.
        """
        self._core.load_connector(temporary)

    def _truncate_head_columns(self, df: DataFrameType, max_size=25) -> DataFrameType:
        """
        Truncate the columns of the dataframe to a maximum of 20 characters.

        Args:
            df (DataFrameType): Pandas or Polars dataframe

        Returns:
            DataFrameType: Pandas or Polars dataframe
        """

        if df_type(df) == "pandas":
            df_trunc = df.copy()

            for col in df.columns:
                if df[col].dtype == "object":
                    first_val = df[col].iloc[0]
                    if isinstance(first_val, str) and len(first_val) > max_size:
                        df_trunc[col] = df_trunc[col].str.slice(0, max_size - 3) + "..."
        elif df_type(df) == "polars":
            try:
                import polars as pl

                df_trunc = df.clone()

                for col in df.columns:
                    if df[col].dtype == pl.Utf8:
                        first_val = df[col][0]
                        if isinstance(first_val, str) and len(df_trunc[col]) > max_size:
                            df_trunc[col] = (
                                df_trunc[col].str.slice(0, max_size - 3) + "..."
                            )
            except ImportError:
                raise ImportError(
                    "Polars is not installed. "
                    "Please install Polars to use this feature."
                )

        return df_trunc

    def _get_sample_head(self) -> DataFrameType:
        head = None
        rows_to_display = 0 if self.lake.config.enforce_privacy else 5
        if self._sample_head is not None:
            head = self.sample_head
        elif not self._core._df_loaded and self.connector:
            head = self.connector.head()
        else:
            head = self.dataframe.head(rows_to_display)

        if head is None:
            return None

        sampler = DataSampler(head)
        sampled_head = sampler.sample(rows_to_display)

        return self._truncate_head_columns(sampled_head)

    def _load_from_config(self, name: str):
        """
        Loads a saved dataframe configuration
        """

        config_manager = DfConfigManager(self)
        return config_manager.load(name)

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

    def validate(self, schema: pydantic.BaseModel):
        """
        Validates Dataframe rows on the basis Pydantic schema input
        (Args):
            schema: Pydantic schema class
            verbose: Print Errors
        """
        df_validator = DfValidator(self.dataframe)
        return df_validator.validate(schema)

    @property
    def lake(self) -> SmartDatalake:
        return self._lake

    @lake.setter
    def lake(self, lake: SmartDatalake):
        self._lake = lake

    @property
    def rows_count(self):
        if self._core._df_loaded:
            return self.dataframe.shape[0]
        elif self.connector is not None:
            return self.connector.rows_count
        else:
            raise ValueError(
                "Cannot determine rows_count. No dataframe or connector loaded."
            )

    @property
    def columns_count(self):
        if self._core._df_loaded:
            return self.dataframe.shape[1]
        elif self.connector is not None:
            return self.connector.columns_count
        else:
            raise ValueError(
                "Cannot determine columns_count. No dataframe or connector loaded."
            )

    @cached_property
    def head_df(self):
        """
        Get the head of the dataframe as a dataframe.

        Returns:
            DataFrameType: Pandas or Polars dataframe
        """
        return self._get_sample_head()

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
    def last_code_executed(self):
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

    def original_import(self):
        return self._original_import

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
    def save_logs(self):
        return self.lake.save_logs

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        self.lake.save_logs = save_logs

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
    def enable_cache(self):
        return self.lake.enable_cache

    @enable_cache.setter
    def enable_cache(self, enable_cache: bool):
        self.lake.enable_cache = enable_cache

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

    @property
    def sample_head(self):
        data = StringIO(self._sample_head)
        return pd.read_csv(data)

    @sample_head.setter
    def sample_head(self, sample_head: pd.DataFrame):
        self._sample_head = sample_head.to_csv(index=False)

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
