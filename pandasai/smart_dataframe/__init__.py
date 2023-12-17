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
import pydantic

from pandasai.helpers.df_validator import DfValidator
from pandasai.skills import skill

from ..smart_datalake import SmartDatalake
from ..schemas.df_config import Config

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from typing import List, Union, Optional
from .abstract_df import DataframeAbstract
from ..connectors.base import BaseConnector

from .df_head import DataframeHead
from .dataframe_proxy import DataframeProxy


class SmartDataframe(DataframeAbstract, Shortcuts):
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
            df (Union[pd.DataFrame, pl.DataFrame]): Pandas or Polars dataframe
            name (str, optional): Name of the dataframe. Defaults to None.
            description (str, optional): Description of the dataframe. Defaults to "".
            custom_head (pd.DataFrame, optional): Sample head of the dataframe.
            config (Config, optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """

        # Define the dataframe proxy
        self.dataframe_proxy = DataframeProxy(df, logger)

        # Define the smart datalake
        self.lake = SmartDatalake([self], config, logger)
        self.lake.set_instance_type(self.__class__.__name__)

        # Set the df info
        self.table_name = name
        if self.table_name is None and self.connector:
            self.table_name = self.connector.fallback_name

        self.table_description = description

        self.head_df = DataframeHead(
            self.dataframe_proxy.connector,
            custom_head,
            samples_amount=0 if self.lake.config.enforce_privacy else 3,
        )

    def add_skills(self, *skills: List[skill]):
        """
        Add Skills to PandasAI
        """
        self.lake.add_skills(*skills)

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
                        pandas dataframe as a response object
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
        if self.dataframe_proxy is None and self.connector:
            return self.connector.column_hash

        columns_str = "".join(self.dataframe.columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    def validate(self, schema: pydantic.BaseModel):
        """
        Validates Dataframe rows on the basis Pydantic schema input
        (Args):
            schema: Pydantic schema class
            verbose: Print Errors
        """
        df_validator = DfValidator(self.dataframe_proxy)
        return df_validator.validate(schema)

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

    @property
    def last_prompt(self):
        return self.lake.last_prompt

    @property
    def last_code_generated(self):
        return self.lake.last_code_generated

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
    def logs(self):
        return self.lake.logs

    @property
    def llm(self):
        return self.lake.llm

    @property
    def last_query_log_id(self):
        return self.lake.last_query_log_id

    def __getattr__(self, name):
        return self.dataframe_proxy.__getattribute__(name)

    def __getitem__(self, key):
        return self.dataframe_proxy.__getitem__(key)

    def __setitem__(self, key, value):
        return self.dataframe_proxy.__setitem__(key, value)

    def __dir__(self):
        return dir(self.dataframe_proxy) + dir(self.__class__)

    def __repr__(self):
        return self.dataframe_proxy.__repr__()

    def __len__(self):
        return self.dataframe_proxy.connector.rows_count

    def __eq__(self, other):
        return self.dataframe_proxy.connector.equals(other.dataframe_proxy.connector)

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
