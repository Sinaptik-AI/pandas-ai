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
from ..helpers.anonymizer import anonymize_dataframe_head
from ..helpers.cache import Cache
from ..helpers.df_config import Config
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

    last_code_generated: str
    last_code_executed: str
    last_result: list

    def __init__(
        self,
        dfs: List[Union[DataFrameType, Any]],
        config: Config = None,
        logger: Logger = None,
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
                smart_dfs.append(SmartDataframe(df, config, logger))
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

    def _get_dfs_data_for_prompt(self):
        rows_to_display = 0 if self._config.enforce_privacy else 5

        result = []
        for df in self._dfs:
            df_head = df.head(rows_to_display)

            if self._config.anonymize_dataframe:
                df_head = anonymize_dataframe_head(df_head)

            df_head_csv = df_head.to_csv(index=False)
            num_rows = df.shape[0]
            num_columns = df.shape[1]

            df_dict = {
                "df_head": df_head_csv,
                "num_rows": num_rows,
                "num_columns": num_columns,
            }
            result.append(df_dict)
        return result

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

        try:
            if self._config.enable_cache and self._cache and self._cache.get(query):
                self._logger.log("Using cached response")
                code = self._cache.get(query)
            else:
                dfs = self._get_dfs_data_for_prompt()

                generate_code_instruction = self._config.custom_prompts.get(
                    "generate_python_code", GeneratePythonCodePrompt
                )(
                    prompt=query,
                    dfs=dfs,
                    # TODO: find a better way to determine the engine
                    engine=self._dfs[0].engine,
                )
                code = self._llm.generate_code(
                    generate_code_instruction,
                    query,
                )

                self._original_instructions = {
                    "question": query,
                    "dfs": dfs,
                }

                if self._config.enable_cache and self._cache:
                    self._cache.set(query, code)

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

    def _format_results(self, results: str) -> str:
        if len(results) > 1:
            output = results[1]

            if output["type"] == "dataframe":
                from ..smart_dataframe import SmartDataframe

                return SmartDataframe(output["result"], config=self._config.__dict__)
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

        error_correcting_instruction = self._config.custom_prompts.get(
            "correct_error", CorrectErrorPrompt
        )(
            code=code,
            error_returned=e,
            question=self._original_instructions["question"],
            # TODO: make it so we pass all the heads and info
            df_head=self._original_instructions["dfs"][0]["df_head"],
            num_rows=self._original_instructions["num_rows"],
            num_columns=self._original_instructions["num_columns"],
        )

        return self._llm.generate_code(error_correcting_instruction, "")

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
