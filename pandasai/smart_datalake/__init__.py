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
from ..helpers.df_config import Config
from ..prompts.base import Prompt
from ..prompts.correct_error_prompt import CorrectErrorPrompt
from ..prompts.generate_python_code import GeneratePythonCodePrompt
from typing import Union, List, Any
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
    _original_instructions: None
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

        from ..smart_dataframe import SmartDataframe

        smart_dfs = []
        for df in dfs:
            if not isinstance(df, SmartDataframe):
                smart_dfs.append(SmartDataframe(df, config, logger, memory))
            else:
                smart_dfs.append(df)

        self._dfs = smart_dfs

        if config:
            self.load_config(config)

        if logger:
            self._logger = logger
        else:
            self._logger = Logger(
                save_logs=self._config.save_logs, verbose=self._config.verbose
            )

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

    def load_config(self, config: Config):
        """
        Load a config to be used to run the queries.

        Args:
            config (Config): Config to be used
        """

        if config["llm"]:
            self.load_llm(config["llm"])

        # TODO: fallback to default config from pandasai
        self._config = Config(**config)

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

    # TODO: figure out a way to handle the cache more effectively
    # i.e. multiple dataframes, etc... Should it be handled at the library level?
    def clear_cache(self):
        """
        Clears the cache of the PandasAI instance.
        """
        if self._cache:
            self._cache.clear()

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

    def _get_prompt(self, key: str, default_prompt: Prompt, default_values: dict = {}):
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
                and self._cache.get(self._memory.get_conversation())
            ):
                self._logger.log("Using cached response")
                code = self._cache.get(self._memory.get_conversation())
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
                    self._cache.set(self._memory.get_conversation(), code)

            if self._config.callback is not None:
                self._config.callback.on_code(code)

            self._original_instructions = {
                "conversation": self._memory.get_conversation(),
                "dfs": self._dfs,
            }

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
            results = []
            while count < self._config.max_retries:
                try:
                    # Execute the code
                    results = self._code_manager.execute_code(
                        code=code_to_run,
                        prompt_id=self._last_prompt_id,
                    )
                    break
                except Exception as e:
                    if not self._config.use_error_correction_framework:
                        raise e

                    count += 1

                    code_to_run = self._retry_run_code(code, e)

            if len(results) > 0:
                self.last_result = results
                self._logger.log(f"Answer: {results}")
        except Exception as exception:
            self.last_error = str(exception)
            print(exception)
            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

        self._logger.log(f"Executed in: {time.time() - self._start_time}s")

        return self._format_results(results)

    def _format_results(self, results: str):
        if len(results) > 1:
            output = results[1]

            if output["type"] == "dataframe":
                from ..smart_dataframe import SmartDataframe

                return SmartDataframe(
                    output["result"],
                    config=self._config.__dict__,
                    logger=self._logger,
                    memory=self._memory,
                )
            elif output["type"] == "plot" or output["type"] == "image":
                import matplotlib.pyplot as plt
                import matplotlib.image as mpimg

                # Load the image file
                image = mpimg.imread(output["result"])

                # Display the image
                plt.imshow(image)
                plt.axis("off")
                plt.show(block=self._is_running_in_console())
                plt.close("all")
            else:
                return output["result"]

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
            "conversation": self._original_instructions["conversation"],
            # TODO: find a better way to determine these values
            "df_head": self._original_instructions["dfs"][0].head_csv,
            "num_rows": self._original_instructions["dfs"][0].rows_count,
            "num_columns": self._original_instructions["dfs"][0].columns_count,
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
