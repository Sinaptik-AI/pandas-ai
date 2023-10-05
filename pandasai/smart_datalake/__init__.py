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

import time
import uuid
import logging
import os
import traceback

from ..helpers.output_types import output_type_factory
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
from ..prompts.generate_python_code import GeneratePythonCodePrompt
from typing import Union, List, Any, Type, Optional
from ..helpers.code_manager import CodeManager
from ..middlewares.base import Middleware
from ..helpers.df_info import DataFrameType
from ..helpers.path import find_project_root


class SmartDatalake:
    _dfs: List[DataFrameType]
    _config: Union[Config, dict]
    _llm: LLM
    _cache: Cache = None
    _logger: Logger
    _start_time: float
    _last_prompt_id: uuid.UUID
    _code_manager: CodeManager
    _memory: Memory

    _last_code_generated: str
    _last_result: str = None
    _last_error: str = None

    def __init__(
        self,
        dfs: List[Union[DataFrameType, Any]],
        config: Optional[Union[Config, dict]] = None,
        logger: Logger = None,
        memory: Memory = None,
        cache: Cache = None,
    ):
        """
        Args:
            dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
            config (Union[Config, dict], optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """

        self.initialize()

        self._load_config(config)

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(
                save_logs=self._config.save_logs, verbose=self._config.verbose
            )

        self._load_dfs(dfs)

        if memory:
            self._memory = memory
        else:
            self._memory = Memory()

        self._code_manager = CodeManager(
            dfs=self._dfs,
            config=self._config,
            logger=self.logger,
        )

        if cache:
            self._cache = cache
        elif self._config.enable_cache:
            self._cache = Cache()

        context = Context(self._config, self.logger, self.engine)

        if self._config.response_parser:
            self._response_parser = self._config.response_parser(context)
        else:
            self._response_parser = ResponseParser(context)

    def initialize(self):
        """Initialize the SmartDatalake"""

        # Create exports/charts folder if it doesn't exist
        try:
            charts_dir = os.path.join((find_project_root()), "exports", "charts")
        except ValueError:
            charts_dir = os.path.join(os.getcwd(), "exports", "charts")
        os.makedirs(charts_dir, mode=0o777, exist_ok=True)

        # Create /cache folder if it doesn't exist
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

    def _load_dfs(self, dfs: List[Union[DataFrameType, Any]]):
        """
        Load all the dataframes to be used in the smart datalake.

        Args:
            dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
        """

        from ..smart_dataframe import SmartDataframe

        smart_dfs = []
        for df in dfs:
            if not isinstance(df, SmartDataframe):
                smart_dfs.append(
                    SmartDataframe(df, config=self._config, logger=self.logger)
                )
            else:
                smart_dfs.append(df)
        self._dfs = smart_dfs

    def _load_config(self, config: Union[Config, dict]):
        """
        Load a config to be used to run the queries.

        Args:
            config (Union[Config, dict]): Config to be used
        """

        config = load_config(config)

        if config.get("llm"):
            self._load_llm(config["llm"])
            config["llm"] = self._llm

        self._config = Config(**config)

    def _load_llm(self, llm: LLM):
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

        self._llm = llm

    def add_middlewares(self, *middlewares: Optional[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: Middlewares to be added
        """
        self._code_manager.add_middlewares(*middlewares)

    def _start_timer(self):
        """Start the timer"""

        self._start_time = time.time()

    def _assign_prompt_id(self):
        """Assign a prompt ID"""

        self._last_prompt_id = uuid.uuid4()

        if self.logger:
            self.logger.log(f"Prompt ID: {self._last_prompt_id}")

    def _get_prompt(
        self,
        key: str,
        default_prompt: Type[AbstractPrompt],
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

        custom_prompt = self._config.custom_prompts.get(key)
        prompt = custom_prompt if custom_prompt else default_prompt()

        # set default values for the prompt
        if "dfs" not in default_values:
            prompt.set_var("dfs", self._dfs)
        if "conversation" not in default_values:
            prompt.set_var("conversation", self._memory.get_conversation())
        for key, value in default_values.items():
            prompt.set_var(key, value)

        self.logger.log(f"Using prompt: {prompt}")

        return prompt

    def _get_cache_key(self) -> str:
        """
        Return the cache key for the current conversation.

        Returns:
            str: The cache key for the current conversation
        """
        cache_key = self._memory.get_conversation()

        # make the cache key unique for each combination of dfs
        for df in self._dfs:
            hash = df.column_hash()
            cache_key += str(hash)

        return cache_key

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
                        pandas/polars dataframe as a response object
                    * plot - specifies that user expects LLM to build
                        a plot
                    * string - specifies that user expects to get text
                        as a response object
                If none `output_type` is specified, the type can be any
                of the above or "text".

        Raises:
            ValueError: If the query is empty
        """

        self._start_timer()

        self.logger.log(f"Question: {query}")
        self.logger.log(f"Running PandasAI with {self._llm.type} LLM...")

        self._assign_prompt_id()

        self._memory.add(query, True)

        try:
            output_type_helper = output_type_factory(output_type, logger=self.logger)

            if (
                self._config.enable_cache
                and self._cache
                and self._cache.get(self._get_cache_key())
            ):
                self.logger.log("Using cached response")
                code = self._cache.get(self._get_cache_key())
            else:
                default_values = {
                    # TODO: find a better way to determine the engine,
                    "engine": self._dfs[0].engine,
                    "output_type_hint": output_type_helper.template_hint,
                }

                generate_python_code_instruction = self._get_prompt(
                    "generate_python_code",
                    default_prompt=GeneratePythonCodePrompt,
                    default_values=default_values,
                )

                code = self._llm.generate_code(generate_python_code_instruction)

                if self._config.enable_cache and self._cache:
                    self._cache.set(self._get_cache_key(), code)

            if self._config.callback is not None:
                self._config.callback.on_code(code)

            self.last_code_generated = code
            self.logger.log(
                f"""Code generated:
```
{code}
```
"""
            )

            retry_count = 0
            code_to_run = code
            result = None
            while retry_count < self._config.max_retries:
                try:
                    # Execute the code
                    result = self._code_manager.execute_code(
                        code=code_to_run,
                        prompt_id=self._last_prompt_id,
                    )
                    break
                except Exception as e:
                    if (
                        not self._config.use_error_correction_framework
                        or retry_count >= self._config.max_retries - 1
                    ):
                        raise e

                    retry_count += 1

                    self._logger.log(
                        f"Failed to execute code with a correction framework "
                        f"[retry number: {retry_count}]",
                        level=logging.WARNING,
                    )

                    traceback_error = traceback.format_exc()
                    code_to_run = self._retry_run_code(code, traceback_error)

            if result is not None:
                if isinstance(result, dict):
                    validation_ok, validation_logs = output_type_helper.validate(result)
                    if not validation_ok:
                        self.logger.log(
                            "\n".join(validation_logs), level=logging.WARNING
                        )

                self.last_result = result
                self.logger.log(f"Answer: {result}")
        except Exception as exception:
            self.last_error = str(exception)
            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

        self.logger.log(f"Executed in: {time.time() - self._start_time}s")

        self._add_result_to_memory(result)

        return self._response_parser.parse(result)

    def _add_result_to_memory(self, result: dict):
        """
        Add the result to the memory.

        Args:
            result (dict): The result to add to the memory
        """
        if result is None:
            return

        if result["type"] == "string" or result["type"] == "number":
            self._memory.add(result["value"], False)
        elif result["type"] == "dataframe" or result["type"] == "plot":
            self._memory.add("Ok here it is", False)

    def _retry_run_code(self, code: str, e: Exception):
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
            "engine": self._dfs[0].engine,
            "code": code,
            "error_returned": e,
        }
        error_correcting_instruction = self._get_prompt(
            "correct_error",
            default_prompt=CorrectErrorPrompt,
            default_values=default_values,
        )

        code = self._llm.generate_code(error_correcting_instruction)
        if self._config.callback is not None:
            self._config.callback.on_code(code)
        return code

    def clear_memory(self):
        """
        Clears the memory
        """
        self._memory.clear()

    @property
    def engine(self):
        return self._dfs[0].engine

    @property
    def last_prompt(self):
        return self._llm.last_prompt

    @property
    def last_prompt_id(self) -> str:
        """Return the id of the last prompt that was run."""
        if self._last_prompt_id is None:
            raise ValueError("Pandas AI has not been run yet.")
        return self._last_prompt_id

    @property
    def logs(self):
        return self.logger.logs

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    @property
    def config(self):
        return self._config

    @property
    def cache(self):
        return self._cache

    @property
    def middlewares(self):
        return self._code_manager.middlewares

    @property
    def verbose(self):
        return self._config.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._config.verbose = verbose
        self._logger.verbose = verbose

    @property
    def save_logs(self):
        return self._config.save_logs

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        self._config.save_logs = save_logs
        self._logger.save_logs = save_logs

    @property
    def callback(self):
        return self._config.callback

    @callback.setter
    def callback(self, callback: Any):
        self.config.callback = callback

    @property
    def enforce_privacy(self):
        return self._config.enforce_privacy

    @enforce_privacy.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self._config.enforce_privacy = enforce_privacy

    @property
    def enable_cache(self):
        return self._config.enable_cache

    @enable_cache.setter
    def enable_cache(self, enable_cache: bool):
        self._config.enable_cache = enable_cache
        if enable_cache:
            if self.cache is None:
                self._cache = Cache()
        else:
            self._cache = None

    @property
    def use_error_correction_framework(self):
        return self._config.use_error_correction_framework

    @use_error_correction_framework.setter
    def use_error_correction_framework(self, use_error_correction_framework: bool):
        self._config.use_error_correction_framework = use_error_correction_framework

    @property
    def custom_prompts(self):
        return self._config.custom_prompts

    @custom_prompts.setter
    def custom_prompts(self, custom_prompts: dict):
        self._config.custom_prompts = custom_prompts

    @property
    def save_charts(self):
        return self._config.save_charts

    @save_charts.setter
    def save_charts(self, save_charts: bool):
        self._config.save_charts = save_charts

    @property
    def save_charts_path(self):
        return self._config.save_charts_path

    @save_charts_path.setter
    def save_charts_path(self, save_charts_path: str):
        self._config.save_charts_path = save_charts_path

    @property
    def custom_whitelisted_dependencies(self):
        return self._config.custom_whitelisted_dependencies

    @custom_whitelisted_dependencies.setter
    def custom_whitelisted_dependencies(
        self, custom_whitelisted_dependencies: List[str]
    ):
        self._config.custom_whitelisted_dependencies = custom_whitelisted_dependencies

    @property
    def max_retries(self):
        return self._config.max_retries

    @max_retries.setter
    def max_retries(self, max_retries: int):
        self._config.max_retries = max_retries

    @property
    def llm(self):
        return self._llm

    @llm.setter
    def llm(self, llm: LLM):
        self._load_llm(llm)

    @property
    def last_code_generated(self):
        return self._last_code_generated

    @last_code_generated.setter
    def last_code_generated(self, last_code_generated: str):
        self._last_code_generated = last_code_generated

    @property
    def last_code_executed(self):
        return self._code_manager.last_code_executed

    @property
    def last_result(self):
        return self._last_result

    @last_result.setter
    def last_result(self, last_result: str):
        self._last_result = last_result

    @property
    def last_error(self):
        return self._last_error

    @last_error.setter
    def last_error(self, last_error: str):
        self._last_error = last_error

    @property
    def dfs(self):
        return self._dfs

    @property
    def memory(self):
        return self._memory
