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

from ..smart_datalake import SmartDatalake
from ..schemas.df_config import Config
from ..helpers.data_sampler import DataSampler

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.df_config_manager import DfConfigManager
from ..helpers.from_google_sheets import from_google_sheets
from typing import List, Union
from ..middlewares.base import Middleware
from ..helpers.df_info import DataFrameType, df_type
from .abstract_df import DataframeAbstract
from ..callbacks.base import BaseCallback
from ..llm import LLM, LangchainLLM


class SmartDataframe(DataframeAbstract, Shortcuts):
    _engine: str
    _original_import: any
    _name: str
    _description: str
    _df: pd.DataFrame
    _dl: SmartDatalake
    _sample_head: str = None

    def __init__(
        self,
        df: DataFrameType,
        name: str = None,
        description: str = None,
        config: Config = None,
        sample_head: pd.DataFrame = None,
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
        self._original_import = df
        self._name = name
        self._description = description

        self._load_df(df)

        self._load_engine()

        self._dl = SmartDatalake([self], config=config, logger=logger)

        if sample_head is not None:
            self._sample_head = sample_head.to_csv(index=False)

    def _load_df(self, df: DataFrameType):
        """
        Load a dataframe into the smart dataframe

        Args:
            df (DataFrameType): Pandas or Polars dataframe or path to a file
        """
        if isinstance(df, str):
            if not (
                df.endswith(".csv")
                or df.endswith(".parquet")
                or df.endswith(".xlsx")
                or df.startswith("https://docs.google.com/spreadsheets/")
            ):
                df_config = self._load_from_config(df)
                if df_config:
                    if self._name is None:
                        self._name = df_config["name"]
                    if self._description is None:
                        self._description = df_config["description"]
                    df = df_config["import_path"]
                else:
                    raise ValueError(
                        "Could not find a saved dataframe configuration "
                        "with the given name."
                    )

            self._df = self._import_from_file(df)
        elif isinstance(df, pd.Series):
            self._df = df.to_frame()
        elif isinstance(df, (list, dict)):
            # if the list can be converted to a dataframe, convert it
            # otherwise, raise an error
            try:
                self._df = pd.DataFrame(df)
            except ValueError:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                )
        else:
            self._df = df

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
        self._engine = df_type(self._df)

        if self._engine is None:
            raise ValueError(
                "Invalid input data. Must be a Pandas or Polars dataframe."
            )

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in dir(SmartDataframe):
            return object.__getattribute__(self, name)
        elif hasattr(self._df, name):
            return getattr(self._df, name)
        else:
            raise AttributeError(
                f"'{name}' is not a valid attribute for SmartDataframe"
            )

    def __dir__(self):
        return dir(self._df)

    def __getitem__(self, key):
        return self._df[key]

    def __setitem__(self, key, value):
        self._df[key] = value

    def __repr__(self):
        return self._df.__repr__()

    def add_middlewares(self, *middlewares: List[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: A list of middlewares

        """
        self._dl.add_middlewares(*middlewares)

    def chat(self, query: str):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe

        Raises:
            ValueError: If the query is empty
        """
        return self._dl.chat(query)

    def column_hash(self) -> str:
        columns_str = "".join(self._df.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    def save(self, name: str = None):
        """
        Saves the dataframe configuration to be used for later
        """

        config_manager = DfConfigManager(self)
        config_manager.save(name)

    def _load_from_config(self, name: str):
        """
        Loads a saved dataframe configuration
        """

        config_manager = DfConfigManager(self)
        return config_manager.load(name)

    def _get_head_csv(self):
        """
        Get the head of the dataframe as a CSV string.

        Returns:
            str: CSV string
        """
        if self._sample_head is not None:
            return self._sample_head

        rows_to_display = 0 if self._dl.config.enforce_privacy else 5

        sample = DataSampler(self._df)
        df_head = sample.sample(rows_to_display)

        self._sample_head = df_head.to_csv(index=False)
        return self._sample_head

    @property
    def datalake(self):
        return self._dl

    @property
    def rows_count(self):
        return self._df.shape[0]

    @property
    def columns_count(self):
        return self._df.shape[1]

    @property
    def head_csv(self):
        return self._get_head_csv()

    @property
    def last_prompt(self):
        return self._dl.last_prompt

    @property
    def last_prompt_id(self) -> str:
        return self._dl.last_prompt_id

    @property
    def last_code_generated(self):
        return self._dl.last_code_generated

    @property
    def last_code_executed(self):
        return self._dl.last_code_executed

    @property
    def last_result(self):
        return self._dl.last_result

    @property
    def last_error(self):
        return self._dl.last_error

    @property
    def original(self):
        return self._df

    @property
    def original_import(self):
        return self._original_import

    @property
    def name(self):
        return self._name

    @property
    def engine(self):
        return self._engine

    @property
    def description(self):
        return self._description

    @property
    def config(self):
        return self._dl.config

    @property
    def cache(self):
        return self._dl.cache

    @property
    def middlewares(self):
        return self._dl.middlewares

    @property
    def logs(self):
        return self._dl.logs

    @property
    def verbose(self):
        return self._dl.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._dl.verbose = verbose

    @property
    def save_logs(self):
        return self._dl.save_logs

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        self._dl.save_logs = save_logs

    @property
    def callback(self):
        return self._dl.callback

    @callback.setter
    def callback(self, callback: BaseCallback):
        self._dl.callback = callback

    @property
    def enforce_privacy(self):
        return self._dl.enforce_privacy

    @enforce_privacy.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self._dl.enforce_privacy = enforce_privacy

    @property
    def enable_cache(self):
        return self._dl.enable_cache

    @enable_cache.setter
    def enable_cache(self, enable_cache: bool):
        self._dl.enable_cache = enable_cache

    @property
    def use_error_correction_framework(self):
        return self._dl.use_error_correction_framework

    @use_error_correction_framework.setter
    def use_error_correction_framework(self, use_error_correction_framework: bool):
        self._dl.use_error_correction_framework = use_error_correction_framework

    @property
    def custom_prompts(self):
        return self._dl.custom_prompts

    @custom_prompts.setter
    def custom_prompts(self, custom_prompts: dict):
        self._dl.custom_prompts = custom_prompts

    @property
    def save_charts(self):
        return self._dl.save_charts

    @save_charts.setter
    def save_charts(self, save_charts: bool):
        self._dl.save_charts = save_charts

    @property
    def save_charts_path(self):
        return self._dl.save_charts_path

    @save_charts_path.setter
    def save_charts_path(self, save_charts_path: str):
        self._dl.save_charts_path = save_charts_path

    @property
    def custom_whitelisted_dependencies(self):
        return self._dl.custom_whitelisted_dependencies

    @custom_whitelisted_dependencies.setter
    def custom_whitelisted_dependencies(
        self, custom_whitelisted_dependencies: List[str]
    ):
        self._dl.custom_whitelisted_dependencies = custom_whitelisted_dependencies

    @property
    def max_retries(self):
        return self._dl.max_retries

    @max_retries.setter
    def max_retries(self, max_retries: int):
        self._dl.max_retries = max_retries

    @property
    def llm(self):
        return self._dl.llm

    @llm.setter
    def llm(self, llm: Union[LLM, LangchainLLM]):
        self._dl.llm = llm

    @property
    def sample_head(self):
        data = StringIO(self._sample_head)
        return pd.read_csv(data)

    @sample_head.setter
    def sample_head(self, sample_head: pd.DataFrame):
        self._sample_head = sample_head.to_csv(index=False)
