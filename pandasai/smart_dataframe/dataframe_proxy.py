"""
A smart dataframe class is a wrapper around the pandas dataframe that allows you
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

from ..helpers.logger import Logger
from typing import Union
from ..connectors.base import BaseConnector
from ..connectors.pandas import PandasConnector


class DataframeProxy:
    def __init__(self, df: Union[pd.DataFrame, BaseConnector], logger: Logger = None):
        self.logger = logger
        self.load_dataframe(df)
        self.df = None

    def load_dataframe(self, df: Union[pd.DataFrame, BaseConnector]):
        """
        Load the dataframe from a file or a connector.

        Args:
            df (Union[pd.DataFrame, BaseConnector]): The dataframe to load.
        """
        if isinstance(df, BaseConnector):
            self.connector = df
        elif isinstance(df, (pd.DataFrame, pd.Series, list, dict, str)):
            self.connector = PandasConnector({"original_df": df})
        else:
            try:
                import polars as pl

                if isinstance(df, pl.DataFrame):
                    from ..connectors.polars import PolarsConnector

                    self.connector = PolarsConnector({"original_df": df})
                else:
                    raise ValueError(
                        "Invalid input data. We cannot convert it to a dataframe."
                    )
            except ImportError as e:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                ) from e

        self.connector.logger = self.logger

    def load_connector(self, partial: bool = False):
        if self.df is not None and not self.partial:
            return

        self.df = self.connector.execute()
        self.partial = partial

    def __getitem__(self, key):
        self.load_connector()
        return self.df.__getitem__(key)

    def __setitem__(self, key, value):
        self.load_connector()
        return self.df.__setitem__(key, value)

    def __getattribute__(self, name):
        if name in pd.DataFrame.__dict__:
            self.load_connector()
            return object.__getattribute__(self.df, name)

        return object.__getattribute__(self, name)
