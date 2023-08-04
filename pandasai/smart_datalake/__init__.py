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
import sys

from ..llm.base import LLM
from ..llm.langchain import LangchainLLM

from ..helpers.logger import Logger
from ..helpers.cache import Cache
from ..helpers.memory import Memory
from ..helpers.df_config import Config, load_config
from ..prompts.base import Prompt
from ..prompts.correct_error_prompt import CorrectErrorPrompt
from ..prompts.generate_python_code import GeneratePythonCodePrompt
from typing import Union, List, Any, Type, Optional
from ..helpers.code_manager import CodeManager
from ..middlewares.base import Middleware
from ..helpers.df_info import DataFrameType


class SmartDatalake:
    _dfs: List[DataFrameType]
    _config: Config
    _llm: LLM
    _cache: Cache
    _logger: Logger
    _start_time: float
    _last_prompt_id: uuid
    _code_manager: CodeManager
    _memory: Memory

    last_code_generated: str
    last_code_executed: str
    last_result: list

    def __init__(
        self,
        dfs: List[Union[DataFrameType, Any]],
        config: Config = None,
        logger: Logger = None,
        memory: Memory = None,
    ):
        """
        Args:
            dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
            config (Config, optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """

        self._load_config(config)

        if logger:
            self._logger = logger
        else:
            self._logger = Logger(
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
            logger=self._logger,
        )

        if self._config.enable_cache:
            self._cache = Cache()

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
                    SmartDataframe(df, config=self._config, logger=self._logger)
                )
            else:
                smart_dfs.append(df)
        self._dfs = smart_dfs

    def _load_config(self, config: Config):
        """
        Load a config to be used to run the queries.

        Args:
            config (Config): Config to be used
        """

        self._config = load_config(config)

        if self._config.llm:
            self._load_llm(self._config.llm)

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

        try:
            llm.is_pandasai_llm()
        except AttributeError:
            llm = LangchainLLM(llm)

        self._llm = llm

    def add_middlewares(self, *middlewares: List[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: A list of middlewares
        """
        self._code_manager.add_middlewares(*middlewares)

    def _start_timer(self):
        """Start the timer"""

        self._start_time = time.time()

    def _assign_prompt_id(self):
        """Assign a prompt ID"""

        self._last_prompt_id = uuid.uuid4()
        self._logger.log(f"Prompt ID: {self._last_prompt_id}")

    def _is_running_in_console(self) -> bool:
        """
        Check if the code is running in console or not.

        Returns:
            bool: True if running in console else False
        """

        return sys.stdout.isatty()

    def _get_prompt(
        self,
        key: str,
        default_prompt: Type[Prompt],
        default_values: Optional[dict] = None,
    ) -> tuple[Prompt, dict]:
        if default_values is None:
            default_values = {}

        prompt = self._config.custom_prompts.get(key)

        if prompt and isinstance(prompt, type):
            prompt = prompt(**default_values)

        if prompt:
            """Override all the variables with _ prefix with default variable values"""
            for var in prompt._args:
                if var[0] == "_" and var[1:] in default_values:
                    prompt.override_var(var, default_values[var[1:]])

            """Declare the global variables to be used in the prompt with $ prefix"""
            prompt_globals = {"dfs": self._dfs}

            """Replace all variables with $ prefix with evaluated values"""
            prompt_text = prompt.text.split(" ")
            for i in range(len(prompt_text)):
                word = prompt_text[i]

                if word.startswith("$"):
                    prompt_text[i] = str(eval(word[1:], prompt_globals))
            prompt.text = " ".join(prompt_text)

            return prompt, prompt._args

        return default_prompt(**default_values, dfs=self._dfs), default_values

    def _get_cache_key(self) -> str:
        cache_key = self._memory.get_conversation()

        # make the cache key unique for each combination of dfs
        for df in self._dfs:
            cache_key += df.column_hash()

        return cache_key

    def chat(self, query: str):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe

        Raises:
            ValueError: If the query is empty
        """

        self._start_timer()

        self._logger.log(f"Question: {query}")
        self._logger.log(f"Running PandasAI with {self._llm.type} LLM...")

        self._assign_prompt_id()

        self._memory.add(query, True)

        try:
            if (
                self._config.enable_cache
                and self._cache
                and self._cache.get(self._get_cache_key())
            ):
                self._logger.log("Using cached response")
                code = self._cache.get(self._get_cache_key())
            else:
                default_values = {
                    "conversation": self._memory.get_conversation(),
                    # TODO: find a better way to determine the engine,
                    "engine": self._dfs[0].engine,
                }
                generate_response_instruction, _ = self._get_prompt(
                    "generate_response",
                    default_prompt=GeneratePythonCodePrompt,
                    default_values=default_values,
                )

                code = self._llm.generate_code(generate_response_instruction)

                if self._config.enable_cache and self._cache:
                    self._cache.set(self._get_cache_key(), code)

            if self._config.callback is not None:
                self._config.callback.on_code(code)

            self.last_code_generated = code
            self._logger.log(
                f"""
                    Code generated:
                    ```
                    {code}
                    ```
                """
            )

            # TODO: figure out what to do with this
            # if show_code and self._in_notebook:
            #     self.notebook.create_new_cell(code)

            count = 0
            code_to_run = code
            result = None
            while count < self._config.max_retries:
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
                        or count >= self._config.max_retries - 1
                    ):
                        raise e

                    count += 1

                    code_to_run = self._retry_run_code(code, e)

            if result is None:
                self.last_result = result
                self._logger.log(f"Answer: {result}")
        except Exception as exception:
            self.last_error = str(exception)
            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

        self._logger.log(f"Executed in: {time.time() - self._start_time}s")

        self._add_result_to_memory(result)

        return self._format_results(result)

    def _add_result_to_memory(self, result: dict):
        if result is None:
            return

        if result["type"] == "string":
            self._memory.add(result["result"], False)
        elif result["type"] == "dataframe":
            self._memory.add("Here is the data you requested.", False)
        elif result["type"] == "plot" or result["type"] == "image":
            self._memory.add("Here is the plot you requested.", False)

    def _format_results(self, result: dict):
        if result is None:
            return

        if result["type"] == "dataframe":
            from ..smart_dataframe import SmartDataframe

            return SmartDataframe(
                result["value"]._df,
                config=self._config.__dict__,
                logger=self._logger,
            )
        elif result["type"] == "plot":
            import matplotlib.pyplot as plt
            import matplotlib.image as mpimg

            # Load the image file
            image = mpimg.imread(result["value"])

            # Display the image
            plt.imshow(image)
            plt.axis("off")
            plt.show(block=self._is_running_in_console())
            plt.close("all")
        else:
            return result["value"]

    def _retry_run_code(self, code: str, e: Exception):
        """
        A method to retry the code execution with error correction framework.

        Args:
            code (str): A python code
            e (Exception): An exception
            dataframes

        Returns (str): A python code
        """

        self._logger.log(f"Failed with error: {e}. Retrying")

        # show the traceback
        from traceback import print_exc

        print_exc()

        default_values = {
            "code": code,
            "error_returned": e,
            "conversation": self._memory.get_conversation(),
            # TODO: find a better way to determine these values
            "df_head": self._dfs[0].head_csv,
            "num_rows": self._dfs[0].rows_count,
            "num_columns": self._dfs[0].columns_count,
        }
        error_correcting_instruction, _ = self._get_prompt(
            "correct_error",
            default_prompt=CorrectErrorPrompt,
            default_values=default_values,
        )

        code = self._llm.generate_code(error_correcting_instruction)
        if self._config.callback is not None:
            self._config.callback.on_code(code)
        return code

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
        return self._logger.logs

    @property
    def config(self):
        return self._config

    @property
    def cache(self):
        return self._cache

    @property
    def middlewares(self):
        return self._code_manager.middlewares

    @config.setter
    def verbose(self, verbose: bool):
        self._config.verbose = verbose

    @config.setter
    def callback(self, callback: Any):
        self._config.callback = callback

    @config.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self._config.enforce_privacy = enforce_privacy

    @config.setter
    def enable_cache(self, enable_cache: bool):
        self._config.enable_cache = enable_cache

    @config.setter
    def use_error_correction_framework(self, use_error_correction_framework: bool):
        self._config.use_error_correction_framework = use_error_correction_framework

    @config.setter
    def custom_prompts(self, custom_prompts: dict):
        self._config.custom_prompts = custom_prompts

    @config.setter
    def save_charts(self, save_charts: bool):
        self._config.save_charts = save_charts

    @config.setter
    def save_charts_path(self, save_charts_path: str):
        self._config.save_charts_path = save_charts_path

    @config.setter
    def custom_whitelisted_dependencies(
        self, custom_whitelisted_dependencies: List[str]
    ):
        self._config.custom_whitelisted_dependencies = custom_whitelisted_dependencies

    @config.setter
    def max_retries(self, max_retries: int):
        self._config.max_retries = max_retries

    @config.setter
    def llm(self, llm: LLM):
        self._load_llm(llm)
