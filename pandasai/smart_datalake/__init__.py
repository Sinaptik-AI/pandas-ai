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
import logging
import os
from pandasai.constants import DEFAULT_CHART_DIRECTORY, DEFAULT_FILE_PERMISSIONS
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.skills import skill
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from ..pipelines.smart_datalake_chat.generate_smart_datalake_pipeline import (
    GenerateSmartDatalakePipeline,
)

from pandasai.helpers.output_types import output_type_factory
from pandasai.helpers.viz_library_types import viz_lib_type_factory
from pandasai.responses.context import Context
from pandasai.responses.response_parser import ResponseParser
from ..llm.base import LLM
from ..llm.langchain import LangchainLLM
from ..helpers.logger import Logger
from ..helpers.cache import Cache
from ..helpers.memory import Memory
from ..schemas.df_config import Config
from ..config import load_config
from ..prompts.base import AbstractPrompt
from ..prompts.correct_error_prompt import CorrectErrorPrompt
from typing import Union, List, Any, Optional
from ..helpers.code_manager import CodeManager
from ..helpers.path import find_project_root
from ..helpers.viz_library_types.base import VisualizationLibrary
import pandas as pd


class SmartDatalake:
    def __init__(
        self,
        dfs: List[Union[pd.DataFrame, Any]],
        config: Optional[Union[Config, dict]] = None,
        logger: Logger = None,
        memory: Memory = None,
        cache: Cache = None,
    ):
        """
        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe
            config (Union[Config, dict], optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """
        self.last_result = None
        self.viz_lib = VisualizationLibrary.DEFAULT.value
        self.last_code_generated = None
        self.last_prompt_id = None

        self.load_config(config)
        self.initialize()

        self.logger = logger or Logger(
            save_logs=self.config.save_logs, verbose=self.config.verbose
        )
        self.load_dfs(dfs)

        self.memory = memory or Memory()
        self.code_manager = CodeManager(
            dfs=self.dfs,
            config=self.config,
            logger=self.logger,
        )

        self.skills_manager = SkillsManager()

        self.cache = cache or None
        if cache is None and self.config.enable_cache:
            self.cache = Cache()

        context = Context(self.config, self.logger)

        if self.config.response_parser:
            self.response_parser = self.config.response_parser(context)
        else:
            self.response_parser = ResponseParser(context)

        if self.config.data_viz_library:
            self.viz_lib = self.config.data_viz_library.value

        self.conversation_id = uuid.uuid4()

        self.instance = self.__class__.__name__

        self.query_exec_tracker = QueryExecTracker(
            server_config=self.config.log_server,
        )

    def set_instance_type(self, type: str):
        self.instance = type

    def is_related_query(self, flag: bool):
        self.query_exec_tracker.set_related_query(flag)

    def initialize(self):
        """Initialize the SmartDatalake, create auxiliary directories.

        If 'save_charts' option is enabled, create '.exports/charts directory'
        in case if it doesn't exist.
        If 'enable_cache' option is enabled, Create './cache' in case if it
        doesn't exist.

        Returns:
            None
        """

        if self.config.save_charts:
            charts_dir = self.config.save_charts_path

            # Add project root path if save_charts_path is default
            if self.config.save_charts_path == DEFAULT_CHART_DIRECTORY:
                try:
                    charts_dir = os.path.join(
                        (find_project_root()), self.config.save_charts_path
                    )
                    self.config.save_charts_path = charts_dir
                except ValueError:
                    charts_dir = os.path.join(os.getcwd(), self.config.save_charts_path)
            os.makedirs(charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

        if self.config.enable_cache:
            try:
                cache_dir = os.path.join((find_project_root()), "cache")
            except ValueError:
                cache_dir = os.path.join(os.getcwd(), "cache")
            os.makedirs(cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

    def load_dfs(self, dfs: List[Union[pd.DataFrame, Any]]):
        """
        Load all the dataframes to be used in the smart datalake.

        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe
        """

        from ..smart_dataframe import SmartDataframe

        smart_dfs = []
        for df in dfs:
            if not isinstance(df, SmartDataframe):
                smart_dfs.append(
                    SmartDataframe(df, config=self.config, logger=self.logger)
                )
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

        if config.get("llm"):
            self.load_llm(config["llm"])
            config["llm"] = self.llm

        if config.get("data_viz_library"):
            self.load_data_viz_library(config["data_viz_library"])
            config["data_viz_library"] = self.data_viz_library

        self.config = Config(**config)

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
        if hasattr(llm, "_llm_type"):
            llm = LangchainLLM(llm)

        self.llm = llm

    def load_data_viz_library(self, data_viz_library: str):
        """
        Load the appropriate instance for viz library type to use.

        Args:
            data_viz_library (enum): TODO

        Raises:
            TODO
        """

        self.data_viz_library = VisualizationLibrary.DEFAULT.value
        if data_viz_library in (item.value for item in VisualizationLibrary):
            self.data_viz_library = data_viz_library

    def add_skills(self, *skills: List[skill]):
        """
        Add Skills to PandasAI
        """
        self.skills_manager.add_skills(*skills)

    def assign_prompt_id(self):
        """Assign a prompt ID"""

        self.last_prompt_id = uuid.uuid4()

        if self.logger:
            self.logger.log(f"Prompt ID: {self.last_prompt_id}")

    def get_prompt(
        self,
        key: str,
        default_prompt: AbstractPrompt,
        default_values: Optional[dict] = None,
    ) -> AbstractPrompt:
        """
        Return a prompt by key.

        Args:
            key (str): The key of the prompt
            default_prompt (Type[AbstractPrompt]): The default prompt to use
            default_values (Optional[dict], optional): The default values to use for the
                prompt. Defaults to None.

        Returns:
            AbstractPrompt: The prompt
        """
        if default_values is None:
            default_values = {}

        custom_prompt = self.config.custom_prompts.get(key)
        prompt = custom_prompt or default_prompt

        # set default values for the prompt
        prompt.set_config(self.config)
        if "dfs" not in default_values:
            prompt.set_var("dfs", self.dfs)
        if "conversation" not in default_values:
            prompt.set_var("conversation", self.memory.get_conversation())
        if "prev_conversation" not in default_values:
            prompt.set_var("prev_conversation", self.memory.get_previous_conversation())
        if "last_message" not in default_values:
            prompt.set_var("last_message", self.memory.get_last_message())

        # Adds the skills to prompt if exist else display nothing
        skills_prompt = self.skills_manager.prompt_display()
        prompt.set_var("skills", skills_prompt if skills_prompt is not None else "")

        for key, value in default_values.items():
            prompt.set_var(key, value)

        self.logger.log(f"Using prompt: {prompt}")
        return prompt

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

        pipeline_context = self.prepare_context_for_smart_datalake_pipeline(
            query=query, output_type=output_type
        )

        try:
            result = GenerateSmartDatalakePipeline(pipeline_context, self.logger).run()
        except Exception as exception:
            self.last_error = str(exception)
            self.query_exec_tracker.success = False
            self.query_exec_tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

        self.update_intermediate_value_post_pipeline_execution(pipeline_context)

        # publish query tracker
        self.query_exec_tracker.publish()

        return result

    def validate_output(self, result: dict, output_type: Optional[str] = None):
        """
        Validate the output of the code execution.

        Args:
            result (Any): Result of executing the code
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
            (ValueError): If the output is not valid
        """

        output_type_helper = output_type_factory(output_type, logger=self.logger)
        result_is_valid, validation_logs = output_type_helper.validate(result)

        if result_is_valid:
            self.query_exec_tracker.add_step(
                {
                    "type": "Validating Output",
                    "success": True,
                    "message": "Output Validation Successful",
                }
            )
        else:
            self.logger.log("\n".join(validation_logs), level=logging.WARNING)
            self.query_exec_tracker.add_step(
                {
                    "type": "Validating Output",
                    "success": False,
                    "message": "Output Validation Failed",
                }
            )
            raise ValueError("Output validation failed")

    def prepare_context_for_smart_datalake_pipeline(
        self, query: str, output_type: Optional[str] = None
    ) -> PipelineContext:
        """
        Prepare Pipeline Context to initiate Smart Data Lake Pipeline.

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

        Returns:
            PipelineContext: The Pipeline Context to be used by Smart Data Lake Pipeline.
        """

        self.query_exec_tracker.start_new_track()

        self.logger.log(f"Question: {query}")
        self.logger.log(f"Running PandasAI with {self.llm.type} LLM...")

        self.assign_prompt_id()

        self.query_exec_tracker.add_query_info(
            self.conversation_id, self.instance, query, output_type
        )

        self.query_exec_tracker.add_dataframes(self.dfs)

        self.memory.add(query, True)

        output_type_helper = output_type_factory(output_type, logger=self.logger)
        viz_lib_helper = viz_lib_type_factory(self.viz_lib, logger=self.logger)

        pipeline_context = PipelineContext(
            dfs=self.dfs,
            config=self.config,
            memory=self.memory,
            cache=self.cache,
            query_exec_tracker=self.query_exec_tracker,
        )
        pipeline_context.add_intermediate_value("is_present_in_cache", False)
        pipeline_context.add_intermediate_value(
            "output_type_helper", output_type_helper
        )
        pipeline_context.add_intermediate_value("viz_lib_helper", viz_lib_helper)
        pipeline_context.add_intermediate_value(
            "last_code_generated", self.last_code_generated
        )
        pipeline_context.add_intermediate_value("get_prompt", self.get_prompt)
        pipeline_context.add_intermediate_value("last_prompt_id", self.last_prompt_id)
        pipeline_context.add_intermediate_value("skills", self.skills_manager)
        pipeline_context.add_intermediate_value("code_manager", self.code_manager)
        pipeline_context.add_intermediate_value("response_parser", self.response_parser)

        return pipeline_context

    def update_intermediate_value_post_pipeline_execution(
        self, pipeline_context: PipelineContext
    ):
        """
        After the Smart Data Lake Pipeline has executed, update values of Smart Data Lake object.

        Args:
            pipeline_context (PipelineContext): Pipeline Context after the Smart Data Lake pipeline execution

        """
        self.last_code_generated = pipeline_context.get_intermediate_value(
            "last_code_generated"
        )
        self.last_result = pipeline_context.get_intermediate_value("last_result")

    def retry_run_code(self, code: str, e: Exception) -> List:
        """
        A method to retry the code execution with error correction framework.

        Args:
            code (str): A python code
            e (Exception): An exception
            dataframes

        Returns (str): A python code
        """

        self.logger.log(f"Failed with error: {e}. Retrying", logging.ERROR)

        default_values = {
            "code": code,
            "error_returned": e,
        }
        error_correcting_instruction = self.get_prompt(
            "correct_error",
            default_prompt=CorrectErrorPrompt(),
            default_values=default_values,
        )

        return self.llm.generate_code(error_correcting_instruction)

    def clear_memory(self):
        """
        Clears the memory
        """
        self.memory.clear()
        self.conversation_id = uuid.uuid4()

    @property
    def last_prompt(self):
        return self.llm.last_prompt

    @property
    def logs(self):
        return self.logger.logs

    @property
    def last_code_executed(self):
        return self.code_manager.last_code_executed

    @property
    def last_query_log_id(self):
        return self.query_exec_tracker.last_log_id
