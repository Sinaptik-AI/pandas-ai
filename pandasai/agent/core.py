import uuid
import os
from pandasai.constants import DEFAULT_CHART_DIRECTORY, DEFAULT_FILE_PERMISSIONS
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.chat.chat_pipeline_input import (
    ChatPipelineInput,
)
from pandasai.skills import Skill
from ..pipelines.chat.generate_chat_pipeline import (
    GenerateChatPipeline,
)

from pandasai.helpers.output_types import output_type_factory
from ..llm.base import LLM
from ..llm.langchain import LangchainLLM
from ..helpers.logger import Logger
from ..helpers.cache import Cache
from ..helpers.memory import Memory
from ..schemas.df_config import Config
from ..config import load_config
from typing import Union, List, Any, Optional
from ..helpers.path import find_project_root
import pandas as pd
from .callbacks import Callbacks
from ..connectors import BaseConnector, PandasConnector


class AgentCore:
    def __init__(
        self,
        dfs: List[Union[BaseConnector, pd.DataFrame, pd.Series, str, dict, list]],
        config: Optional[Union[Config, dict]] = None,
        logger: Optional[Logger] = None,
        memory: Optional[Memory] = None,
        cache: Optional[Cache] = None,
    ):
        """
        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe
            config (Union[Config, dict], optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """
        self.last_prompt = None
        self.last_prompt_id = None
        self.last_result = None
        self.last_code_generated = None
        self.last_code_executed = None

        config = self.load_config(config)

        self.logger = logger or Logger(
            save_logs=config.save_logs, verbose=config.verbose
        )
        dfs = self.load_dfs(dfs, config)

        self.conversation_id = uuid.uuid4()

        self.callbacks = Callbacks(self)

        self.context = PipelineContext(
            dfs=self.dfs, config=config, memory=memory, cache=cache
        )

        self._pipeline = GenerateChatPipeline(
            self.context,
            self.logger,
            on_prompt_generation=self.callbacks.on_prompt_generation,
            on_code_generation=self.callbacks.on_code_generation,
            on_code_execution=self.callbacks.on_code_execution,
            on_result=self.callbacks.on_result,
        )

    def load_dfs(self, dfs: List[Union[pd.DataFrame, Any]], config: Config = None):
        """
        Load all the dataframes to be used in the agent.

        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe
        """

        connectors = []
        for df in dfs:
            if isinstance(df, BaseConnector):
                connectors.append(df)
            elif isinstance(df, (pd.DataFrame, pd.Series, list, dict, str)):
                connectors.append(PandasConnector({"original_df": df}))
            else:
                try:
                    import polars as pl

                    if isinstance(df, pl.DataFrame):
                        from ..connectors.polars import PolarsConnector

                        connectors.append(PolarsConnector({"original_df": df}))
                    else:
                        raise ValueError(
                            "Invalid input data. We cannot convert it to a dataframe."
                        )
                except ImportError as e:
                    raise ValueError(
                        "Invalid input data. We cannot convert it to a dataframe."
                    ) from e
        self.dfs = connectors

    def load_config(self, config: Union[Config, dict]):
        """
        Load a config to be used to run the queries.

        Args:
            config (Union[Config, dict]): Config to be used
        """

        config = load_config(config)

        if isinstance(config, dict) and config.get("llm") is None:
            config["llm"] = self.load_llm(config["llm"])

        config = Config(**config)

        if config.save_charts:
            charts_dir = config.save_charts_path

            # Add project root path if save_charts_path is default
            if config.save_charts_path == DEFAULT_CHART_DIRECTORY:
                try:
                    charts_dir = os.path.join(
                        (find_project_root()), config.save_charts_path
                    )
                    config.save_charts_path = charts_dir
                except ValueError:
                    charts_dir = os.path.join(os.getcwd(), config.save_charts_path)
            os.makedirs(charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

        if config.enable_cache:
            try:
                cache_dir = os.path.join((find_project_root()), "cache")
            except ValueError:
                cache_dir = os.path.join(os.getcwd(), "cache")
            os.makedirs(cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

        return config

    def load_llm(self, llm: LLM) -> LLM:
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
        if hasattr(llm, "_llm_type"):
            llm = LangchainLLM(llm)
        return llm

    def add_skills(self, *skills: Skill):
        """
        Add Skills to PandasAI
        """
        self.context.skills_manager.add_skills(*skills)

    def assign_prompt_id(self):
        """Assign a prompt ID"""

        self.last_prompt_id = uuid.uuid4()

        if self.logger:
            self.logger.log(f"Prompt ID: {self.last_prompt_id}")

    def chat(
        self,
        query: str,
        output_type: Optional[str] = None,
        is_related_query: bool = True,
    ):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe
            output_type (Optional[str]): Add a hint for LLM which
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
                If none `output_type` is specified, the type can be any
                of the above or "text".

        Raises:
            ValueError: If the query is empty
        """
        self.logger.log(f"Question: {query}")
        self.logger.log(f"Running PandasAI with {self.context.config.llm.type} LLM...")

        self.assign_prompt_id()

        pipeline_input = ChatPipelineInput(
            query,
            output_type_factory(output_type, logger=self.logger),
            self.conversation_id,
            self.last_prompt_id,
            is_related_query,
        )

        return self._pipeline.run(pipeline_input)

    def clear_memory(self):
        """
        Clears the memory
        """
        self.context.memory.clear()
        self.conversation_id = uuid.uuid4()

    @property
    def logs(self):
        return self.logger.logs

    @property
    def last_query_log_id(self):
        return self._pipeline.get_last_track_log_id()

    @property
    def config(self):
        return self.context.config

    @property
    def llm(self):
        return self.context.config.llm

    @property
    def cache(self):
        return self.context.cache

    @property
    def memory(self):
        return self.context.memory

    @property
    def skills_manager(self):
        return self.context.skills_manager

    @property
    def last_error(self):
        return self._pipeline.last_error
