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
import uuid

import pandas as pd
import pydantic

from pandasai.helpers.df_validator import DfValidator
from pandasai.skills import skill

from ..smart_datalake import SmartDatalake
from ..schemas.df_config import Config

from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.df_config_manager import DfConfigManager
from typing import List, Union, Optional
from .abstract_df import DataframeAbstract
from ..connectors.base import BaseConnector
from ..connectors.pandas import PandasConnector

from ..helpers.file_importer import FileImporter
from .df_head import DataframeHead


class SmartDataframeCore:
    """
    A smart dataframe class is a wrapper around the pandas/polars dataframe that allows
    you to query it using natural language. It uses the LLMs to generate Python code
    from natural language and then executes it on the dataframe.
    """

    _df = None
    _temporary_loaded: bool = False

    def __init__(self, df: pd.DataFrame, logger: Logger = None):
        self.logger = logger
        self._load_dataframe(df)

    def _load_dataframe(self, df: Union[pd.DataFrame, BaseConnector]):
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

        self.dataframe = None
        self.connector.logger = self.logger

    def _validate_and_convert_dataframe(
        self, df: Union[pd.DataFrame, str, list, dict]
    ) -> pd.DataFrame:
        """
        Validate the dataframe and convert it to a Pandas or Polars dataframe.

        Args:
            df (Union[pd.DataFrame, str, list, dict]): The dataframe to validate and convert.

        Returns:
            pd.DataFrame: The validated and converted dataframe.
        """
        if isinstance(df, str):
            return FileImporter.import_from_file(df)
        elif isinstance(df, (list, dict)):
            # if the list or dictionary can be converted to a dataframe, convert it
            # otherwise, raise an error
            try:
                return pd.DataFrame(df)
            except ValueError as e:
                raise ValueError(
                    "Invalid input data. We cannot convert it to a dataframe."
                ) from e
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
        self._temporary_loaded = temporary

    def _unload_connector(self):
        """
        Unload the connector from the smart dataframe.
        This is done when a partial dataframe is loaded from a connector (i.e.
        because of a filter) and we want to load the full dataframe or a different
        partial dataframe.
        """
        self._df = None
        self._temporary_loaded = False

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._df is not None:
            return_df = self._df.copy()

            if self._df is not None and self._temporary_loaded:
                self._unload_connector()

            return return_df
        return None

    @dataframe.setter
    def dataframe(self, df: pd.DataFrame):
        """
        Load a dataframe into the smart dataframe

        Args:
            df (pd.DataFrame): The dataframe to load.
        """
        df = self._validate_and_convert_dataframe(df)
        self._df = df


class SmartDataframe(DataframeAbstract, Shortcuts):
    _original_import: any
    _core: SmartDataframeCore

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
        self._original_import = df

        if (
            isinstance(df, str)
            and not df.endswith(".csv")
            and not df.endswith(".parquet")
            and not df.endswith(".xlsx")
            and not df.startswith("https://docs.google.com/spreadsheets/")
        ):
            if not (df_config := self._load_from_config(df)):
                raise ValueError(
                    "Could not find a saved dataframe configuration "
                    "with the given name."
                )

            if "://" in df_config["import_path"]:
                df = self._instantiate_connector(df_config["import_path"])
            else:
                df = df_config["import_path"]

            if name is None:
                name = df_config["name"]
            if description is None:
                description = df_config["description"]
        self._core = SmartDataframeCore(df, logger)

        self.table_description = description
        self.table_name = name
        self.lake = SmartDatalake([self], config, logger)

        # set instance type in SmartDataLake
        self.lake.set_instance_type(self.__class__.__name__)

        # If no name is provided, use the fallback name provided the connector
        if self.table_name is None and self.connector:
            self.table_name = self.connector.fallback_name

        self.head_df = DataframeHead(
            self._core.connector,
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
        if self._core.dataframe is None and self.connector:
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

    def _instantiate_connector(self, import_path: str) -> BaseConnector:
        connector_name = import_path.split("://")[0]
        connector_path = import_path.split("://")[1]
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
        return getattr(
            __import__("pandasai.connectors", fromlist=[connector_name]),
            connector_name,
        )(config=connector_data)

    def _load_from_config(self, name: str):
        """
        Loads a saved dataframe configuration
        """

        config_manager = DfConfigManager(self)
        return config_manager.load(name)

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._core.dataframe

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
    def rows_count(self):
        return self.connector.rows_count

    @property
    def columns_count(self):
        return self.connector.columns_count

    @property
    def last_prompt(self):
        return self.lake.last_prompt

    @property
    def last_prompt_id(self) -> uuid.UUID:
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

    def original_import(self):
        return self._original_import

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
        if name in self._core.__dir__():
            return getattr(self._core, name)
        elif name in self.dataframe.__dir__():
            return getattr(self.dataframe, name)
        else:
            return self.__getattribute__(name)

    def __getattribute__(self, name):
        """
        This method is called whenever any attribute of the object is accessed

        Args:
            name (str): Name of the attribute

        Returns:
            Any: Attribute value
        """
        attr = object.__getattribute__(self, name)

        # Check if the attribute is a method and
        if callable(attr) and name != "load_connector":

            def new_attr(*args, **kwargs):
                # Call self.load_connector() before the actual method
                self.load_connector()
                # Then call the actual method
                return attr(*args, **kwargs)

            return new_attr
        else:
            return attr

    def __getitem__(self, key):
        if self.dataframe is None:
            self.load_connector()

        return self.dataframe.__getitem__(key)

    def __setitem__(self, key, value):
        if self.dataframe is None:
            self.load_connector()

        return self.dataframe.__setitem__(key, value)

    def __dir__(self):
        return dir(self._core) + dir(self.dataframe) + dir(self.__class__)

    def __repr__(self):
        return self.dataframe.__repr__()

    def __len__(self):
        return self._core.connector.rows_count

    def __eq__(self, other):
        return self._core.connector.equals(other._core.connector)

    def get_query_exec_func(self):
        return self._core.connector.execute_direct_sql_query


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
