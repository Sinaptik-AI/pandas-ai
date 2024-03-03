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
import uuid
from functools import cached_property
from io import StringIO
from typing import Any, List, Optional, Union

import pandasai.pandas as pd
from pandasai.agent.base import Agent
from pandasai.connectors.pandas import PandasConnector
from pandasai.helpers.df_validator import DfValidator
from pandasai.pydantic import BaseModel

from ..connectors.base import BaseConnector
from ..helpers.df_info import DataFrameType
from ..helpers.logger import Logger
from ..schemas.df_config import Config
from ..skills import Skill


class SmartDataframe:
    _table_name: str
    _table_description: str
    _custom_head: str = None
    _original_import: any

    def __init__(
        self,
        df: Union[DataFrameType, BaseConnector],
        name: str = None,
        description: str = None,
        custom_head: pd.DataFrame = None,
        config: Config = None,
    ):
        """
        Args:
            df: A supported dataframe type, or a pandasai Connector
            name (str, optional): Name of the dataframe. Defaults to None.
            description (str, optional): Description of the dataframe. Defaults to "".
            custom_head (pd.DataFrame, optional): Sample head of the dataframe.
            config (Config, optional): Config to be used. Defaults to None.
        """
        self._original_import = df

        self._agent = Agent([df], config=config)

        self.dataframe = self._agent.context.dfs[0]

        self._table_description = description
        self._table_name = name

        if custom_head is not None:
            self._custom_head = custom_head.to_csv(index=False)

    def load_dfs(self, df, name: str, description: str, custom_head: pd.DataFrame):
        if isinstance(df, (pd.DataFrame, pd.Series, list, dict, str)):
            df = PandasConnector(
                {"original_df": df},
                name=name,
                description=description,
                custom_head=custom_head,
            )
        else:
            try:
                import polars as pl

                if isinstance(df, pl.DataFrame):
                    from ..connectors.polars import PolarsConnector

                    df = PolarsConnector(
                        {"original_df": df},
                        name=name,
                        description=description,
                        custom_head=custom_head,
                    )
                else:
                    raise ValueError(
                        "Invalid input data. We cannot convert it to a dataframe."
                    )
            except ImportError as e:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                ) from e
        return df

    def add_skills(self, *skills: Skill):
        """
        Add Skills to PandasAI
        """
        self._agent.add_skills(*skills)

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
                        pandas/modin/polars dataframe as a response object
                    * plot - specifies that user expects LLM to build
                        a plot
                    * string - specifies that user expects to get text
                        as a response object

        Raises:
            ValueError: If the query is empty
        """
        return self._agent.chat(query, output_type)

    def validate(self, schema: BaseModel):
        """
        Validates Dataframe rows on the basis Pydantic schema input
        (Args):
            schema: Pydantic schema class
            verbose: Print Errors
        """
        df_validator = DfValidator(self.dataframe)
        return df_validator.validate(schema)

    @cached_property
    def head_df(self):
        """
        Get the head of the dataframe as a dataframe.

        Returns:
            DataFrameType: Pandas, Modin or Polars dataframe
        """
        return self.dataframe.get_head()

    @cached_property
    def head_csv(self):
        """
        Get the head of the dataframe as a CSV string.

        Returns:
            str: CSV string
        """
        df_head = self.dataframe.get_head()
        return df_head.to_csv(index=False)

    @property
    def last_prompt(self):
        return self._agent.last_prompt

    @property
    def last_prompt_id(self) -> uuid.UUID:
        return self._agent.last_prompt_id

    @property
    def last_code_generated(self):
        return self._agent.last_code_executed

    @property
    def last_code_executed(self):
        return self._agent.last_code_executed

    def original_import(self):
        return self._original_import

    @property
    def logger(self):
        return self._agent.logger

    @logger.setter
    def logger(self, logger: Logger):
        self._agent.logger = logger

    @property
    def logs(self):
        return self._agent.context.config.logs

    @property
    def verbose(self):
        return self._agent.context.config.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._agent.context.config.verbose = verbose

    @property
    def save_logs(self):
        return self._agent.context.config.save_logs

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        self._agent.context.config.save_logs = save_logs

    @property
    def enforce_privacy(self):
        return self._agent.context.config.enforce_privacy

    @enforce_privacy.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self._agent.context.config.enforce_privacy = enforce_privacy

    @property
    def enable_cache(self):
        return self._agent.context.config.enable_cache

    @enable_cache.setter
    def enable_cache(self, enable_cache: bool):
        self._agent.context.config.enable_cache = enable_cache

    @property
    def save_charts(self):
        return self._agent.context.config.save_charts

    @save_charts.setter
    def save_charts(self, save_charts: bool):
        self._agent.context.config.save_charts = save_charts

    @property
    def save_charts_path(self):
        return self._agent.context.config.save_charts_path

    @save_charts_path.setter
    def save_charts_path(self, save_charts_path: str):
        self._agent.context.config.save_charts_path = save_charts_path

    @property
    def table_name(self):
        return self._table_name

    @property
    def table_description(self):
        return self._table_description

    @property
    def custom_head(self):
        data = StringIO(self._custom_head)
        return pd.read_csv(data)

    @property
    def last_query_log_id(self):
        return self._agent.last_query_log_id

    def __len__(self):
        return len(self.dataframe)

    def __eq__(self, other):
        return self.dataframe.equals(other.dataframe)

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


def load_smartdataframes(
    dfs: List[Union[DataFrameType, Any]], config: Config
) -> List[SmartDataframe]:
    """
    Load all the dataframes to be used in the smart datalake.

    Args:
        dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
    """

    smart_dfs = []
    for df in dfs:
        if not isinstance(df, SmartDataframe):
            smart_dfs.append(SmartDataframe(df, config=config))
        else:
            smart_dfs.append(df)

    return smart_dfs
