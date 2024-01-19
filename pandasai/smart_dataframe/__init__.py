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

import hashlib

import pandas as pd

from ..schemas.df_config import Config

from ..helpers.logger import Logger
from typing import List, Union
from ..connectors.base import BaseConnector

from .df_head import DataframeHead
from .dataframe_proxy import DataframeProxy


class SmartDataframe:
    def __init__(
        self,
        df: Union[pd.DataFrame, pd.Series, BaseConnector, str, dict, list],
        name: str = None,
        description: str = None,
        custom_head: pd.DataFrame = None,
        config: Config = None,
        logger: Logger = None,
    ):
        """
        Args:
            df: A supported dataframe type, or a pandasai Connector
            name (str, optional): Name of the dataframe. Defaults to None.
            description (str, optional): Description of the dataframe. Defaults to "".
            custom_head (pd.DataFrame, optional): Sample head of the dataframe.
            config (Config, optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """

        if config is None or isinstance(config, dict):
            self.config = Config(**(config or {}))
        else:
            self.config = config

        self.logger = logger or Logger(self.config)

        # Define the dataframe proxy
        self.dataframe_proxy = DataframeProxy(df, logger)

        # Set the df info
        self.table_name = name
        if self.table_name is None and self.connector:
            self.table_name = self.connector.fallback_name
        if self.connector:
            self._table_name = self.connector.fallback_name

        self.table_description = description

        self.head_df = DataframeHead(
            self.dataframe_proxy.connector,
            custom_head,
            samples_amount=0 if self.config.enforce_privacy else 3,
        )

    def column_hash(self) -> str:
        """
        Get the hash of the columns of the dataframe.

        Returns:
            str: Hash of the columns of the dataframe
        """
        if self.dataframe is None:
            self.load_connector()

        if self.dataframe_proxy is None and self.connector:
            return self.connector.column_hash

        columns_str = "".join(self.dataframe.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    @property
    def dataframe(self):
        return self.dataframe_proxy.df

    @property
    def connector(self):
        return self.dataframe_proxy.connector

    @connector.setter
    def connector(self, connector: BaseConnector):
        connector.logger = self.logger
        self.dataframe_proxy.connector = connector

    @property
    def rows_count(self):
        return self.connector.rows_count

    @property
    def columns_count(self):
        return self.connector.columns_count

    def get_query_exec_func(self):
        return self.dataframe_proxy.connector.execute_direct_sql_query

    def load_connector(self, partial: bool = False):
        self.dataframe_proxy.load_connector(partial)


def load_smartdataframes(
    dfs: List[Union[pd.DataFrame, BaseConnector, SmartDataframe, str, dict, list]],
    config: Config = None,
) -> List[SmartDataframe]:
    """
    Load all the dataframes to be used in the smart datalake.

    Args:
        dfs (List[Union[pd.DataFrame, BaseConnector, SmartDataframe, str, dict, list]]):
    """

    smart_dfs = []
    for df in dfs:
        if not isinstance(df, SmartDataframe):
            smart_dfs.append(SmartDataframe(df, config=config))
        else:
            smart_dfs.append(df)

    return smart_dfs
