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

import pandas as pd
from ..smart_datalake import SmartDatalake
from ..helpers.df_config import Config
from ..helpers.anonymizer import anonymize_dataframe_head

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from typing import List
from ..middlewares.base import Middleware
from ..helpers.df_info import DataFrameType, df_type
from .abstract_df import DataframeAbstract


class SmartDataframe(DataframeAbstract, Shortcuts):
    _engine: str
    _name: str
    _description: str
    _df: pd.DataFrame
    _dl: SmartDatalake

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
        self._name = name
        self._description = description

        self._load_df(df)

        self._load_engine()

        self._dl = SmartDatalake([self], config=config, logger=logger)

    def _load_df(self, df: DataFrameType):
        """
        Load a dataframe into the smart dataframe

        Args:
            df (DataFrameType): Pandas or Polars dataframe or path to a file
        """
        if isinstance(df, str):
            self._df = self._import_from_file(df)
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
        else:
            raise ValueError("Invalid file format.")

    def _load_engine(self):
        self._engine = df_type(self._df)

        if self._engine is None:
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

    @property
    def rows_count(self):
        return self._df.shape[0]

    @property
    def columns_count(self):
        return self._df.shape[1]

    @property
    def head_csv(self):
        rows_to_display = 0 if self._dl.config.enforce_privacy else 5

        df_head = self._df.head(rows_to_display)
        if self._dl.config.anonymize_dataframe:
            df_head = anonymize_dataframe_head(df_head)

        return df_head.to_csv(index=False)

    @property
    def last_prompt(self):
        return self._dl.last_prompt

    @property
    def last_code_generated(self):
        return self._dl.last_code_executed

    @property
    def last_result(self):
        return self._dl.last_result

    @property
    def original(self):
        return self._df

    @property
    def name(self):
        return self._name

    @property
    def engine(self):
        return self._engine

    @property
    def description(self):
        return self._description
