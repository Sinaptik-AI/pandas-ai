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
import uuid
import os
from pandasai.constants import DEFAULT_CHART_DIRECTORY, DEFAULT_FILE_PERMISSIONS
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.skills import Skill
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from ..pipelines.smart_datalake_chat.generate_smart_datalake_pipeline import (
    GenerateSmartDatalakePipeline,
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


class SmartDatalake:
    def __init__(
        self,
        dfs: List[Union[pd.DataFrame, Any]],
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
        self.instance = self.__class__.__name__

        self.callbacks = Callbacks(self)

        query_exec_tracker = QueryExecTracker(
            server_config=config.log_server,
        )

        self.context = PipelineContext(
            dfs=self.dfs,
            config=config,
            memory=memory,
            cache=cache,
            query_exec_tracker=query_exec_tracker,
        )

    def set_instance_type(self, type_: str):
        self.instance = type_

    def is_related_query(self, flag: bool):
        self.context.query_exec_tracker.set_related_query(flag)

    def load_dfs(self, dfs: List[Union[pd.DataFrame, Any]], config: Config = None):
        """
        Load all the dataframes to be used in the smart datalake.

        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe
        """

        from ..smart_dataframe import SmartDataframe

        smart_dfs = []
        for df in dfs:
            if not isinstance(df, SmartDataframe):
                smart_dfs.append(SmartDataframe(df, config=config, logger=self.logger))
            else:
                smart_dfs.append(df)
        self.dfs = smart_dfs

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

    def chat(self, query: str, output_type: Optional[str] = None):
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

        self.context.query_exec_tracker.start_new_track()

        self.logger.log(f"Question: {query}")
        self.logger.log(f"Running PandasAI with {self.context.config.llm.type} LLM...")

        self.assign_prompt_id()

        self.context.query_exec_tracker.add_query_info(
            self.conversation_id, self.instance, query, output_type
        )

        self.context.query_exec_tracker.add_dataframes(self.dfs)

        self.context.memory.add(query, True)

        self.prepare_context_for_smart_datalake_pipeline(output_type=output_type)

        try:
            result = GenerateSmartDatalakePipeline(
                self.context,
                self.logger,
                on_prompt_generation=self.callbacks.on_prompt_generation,
                on_code_generation=self.callbacks.on_code_generation,
                on_code_execution=self.callbacks.on_code_execution,
                on_result=self.callbacks.on_result,
            ).run()
        except Exception as exception:
            self.last_error = str(exception)
            self.context.query_exec_tracker.success = False
            self.context.query_exec_tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

        # Publish query tracker
        self.context.query_exec_tracker.publish()

        return result

    def prepare_context_for_smart_datalake_pipeline(
        self, output_type: Optional[str] = None
    ) -> PipelineContext:
        """
        Prepare Pipeline Context to initiate Smart Data Lake Pipeline.

        Args:
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

        Returns:
            PipelineContext: The Pipeline Context to be used by Smart Data Lake Pipeline.
        """
        self.context.add_many(
            {
                "output_type_helper": output_type_factory(
                    output_type, logger=self.logger
                ),
                "last_prompt_id": self.last_prompt_id,
            }
        )

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
        return self.context.query_exec_tracker.last_log_id

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
