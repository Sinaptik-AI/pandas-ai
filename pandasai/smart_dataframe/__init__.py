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
    response = df.query("What is the average loan amount?")
    print(response)
    # The average loan amount is $15,000.
    ```
"""

import pandas as pd
from ..llm.base import LLM
from ..llm.langchain import LangchainLLM
from ..smart_datalake import SmartDatalake

# from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.cache import Cache
from pydantic import BaseModel
from typing import Union, List
from ..middlewares.base import Middleware
from ..middlewares.charts import ChartsMiddleware

polars_imported = False
try:
    import polars as pl

    polars_imported = True
    DataFrameType = Union[pd.DataFrame, pl.DataFrame]
except ImportError:
    DataFrameType = pd.DataFrame


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    anonymize_dataframe: bool = True
    use_error_correction_framework: bool = True
    conversational_answer: bool = False
    custom_prompts: dict = {}
    save_charts: bool = False
    save_charts_path: str = "charts"
    custom_whitelisted_dependencies: List[str] = []
    max_retries: int = 3
    middlewares: List[Middleware] = []
    llm: Union[LLM, LangchainLLM] = None

    class Config:
        arbitrary_types_allowed = True


class SmartDataframe:
    engine: str

    _df: pd.DataFrame
    _dl: SmartDatalake
    _config: Config
    _llm: LLM
    _cache: Cache
    _logger: Logger
    _middlewares: list = [ChartsMiddleware()]

    def __init__(
        self,
        df: DataFrameType,
        config: Config = None,
        logger: Logger = None,
    ):
        """
        Args:
            df (Union[pd.DataFrame, pl.DataFrame]): Pandas or Polars dataframe
            config (Config, optional): Config to be used. Defaults to None.
        """

        self._df = df

        self.load_config(config)

        if logger:
            self._logger = logger
        else:
            self._logger = Logger(
                save_logs=self._config.save_logs, verbose=self._config.verbose
            )

        if self._config.middlewares is not None:
            self.add_middlewares(*self._config.middlewares)

        if self._config.enable_cache:
            self._cache = Cache()

        self.load_engine()

    def load_engine(self):
        if polars_imported and isinstance(self._df, pl.DataFrame):
            self.engine = "polars"
        elif isinstance(self._df, pd.DataFrame):
            self.engine = "pandas"

        if self.engine is None:
            raise ValueError(
                "Invalid input data. Must be a Pandas or Polars dataframe."
            )

    def __getattr__(self, attr):
        return getattr(self._df, attr)

    def __dir__(self):
        return dir(self._df)

    def __getitem__(self, key):
        return self._df[key]

    def __repr__(self):
        return repr(self._df)

    def load_config(self, config: Config):
        """
        Load a config to be used to run the queries.

        Args:
            config (Config): Config to be used
        """

        if config is None:
            self._config = Config()
        else:
            if config["llm"]:
                self.load_llm(config["llm"])

            # TODO: fallback to default config from pandasai
            self._config = Config(**config)

    def load_llm(self, llm: LLM):
        """
        Load a LLM to be used to run the queries.
        Check if it is a PandasAI LLM or a Langchain LLM.
        If it is a Langchain LLM, wrap it in a PandasAI LLM.

        Args:
            llm (object): LLMs option to be used for API access

        Raises:
            BadImportError: If the LLM is a Langchain LLM but the langchain package
            is not installed
        """

        try:
            llm.is_pandasai_llm()
        except AttributeError:
            llm = LangchainLLM(llm)

        self._llm = llm

    def add_middlewares(self, *middlewares: List[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: A list of middlewares

        """
        self._middlewares.extend(middlewares)

    # TODO: figure out a way to handle the cache more effectively
    # i.e. multiple dataframes, etc... Should it be handled at the library level?
    def clear_cache(self):
        """
        Clears the cache of the PandasAI instance.
        """
        if self._cache:
            self._cache.clear()

    def query(self, query: str):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe

        Raises:
            ValueError: If the query is empty
        """
        config_dict = self._config.__dict__
        config_dict["middlewares"] = self._middlewares
        config_dict["llm"] = self._llm
        config = Config(**config_dict).__dict__

        self._dl = SmartDatalake([self], config=config, logger=self._logger)
        return self._dl.query(query)

    @property
    def last_prompt(self):
        return self._llm.last_prompt

    @property
    def last_code_generated(self):
        return self._dl.last_code_executed

    @property
    def last_result(self):
        return self._dl.last_result

    @property
    def original(self):
        return self._df
