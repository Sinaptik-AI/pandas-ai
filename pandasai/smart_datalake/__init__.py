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
    response = df.query("What is the average loan amount?")
    print(response)
    # The average loan amount is $15,000.
    ```
"""

import ast
import time
import uuid
import astor
import re
import sys

import pandas as pd
from ..helpers._optional import import_dependency
from ..llm.base import LLM
from ..llm.langchain import LangchainLLM

# from ..helpers.shortcuts import Shortcuts
from ..helpers.logger import Logger
from ..helpers.anonymizer import anonymize_dataframe_head
from ..helpers.cache import Cache
from ..helpers.save_chart import add_save_chart
from pydantic import BaseModel
from ..prompts.correct_error_prompt import CorrectErrorPrompt
from ..prompts.generate_response import GenerateResponsePrompt
from ..prompts.generate_python_code import GeneratePythonCodePrompt
from typing import Union, List
from ..middlewares.base import Middleware
from ..middlewares.charts import ChartsMiddleware
from ..constants import (
    WHITELISTED_BUILTINS,
    WHITELISTED_LIBRARIES,
)
from ..exceptions import BadImportError

polars_imported = False
try:
    import polars as pl

    polars_imported = True
    DataFrameType = Union[pd.DataFrame, pl.DataFrame]
except ImportError:
    DataFrameType = pd.DataFrame


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    anonymize_dataframe: bool = True
    use_error_correction_framework: bool = True
    conversational_answer: bool = False
    custom_prompts: dict = {}
    save_charts: bool = False
    save_charts_path: str = "charts"
    custom_whitelisted_dependencies: List[str] = []
    max_retries: int = 3
    middlewares: List[Middleware] = []
    llm: Union[LLM, LangchainLLM] = None

    class Config:
        arbitrary_types_allowed = True


class SmartDatalake:
    _dfs: pd.DataFrame
    _config: Config
    _llm: LLM
    _cache: Cache
    _logger: Logger
    _start_time: float
    _last_prompt_id: uuid
    _original_instructions: None
    _middlewares: list = [ChartsMiddleware()]

    last_code_generated: str
    last_code_executed: str
    last_result: list

    def __init__(
        self,
        dfs: List[DataFrameType],
        config: Config = None,
        logger: Logger = None,
    ):
        """
        Args:
            df (Union[pd.DataFrame, pl.DataFrame]): Pandas or Polars dataframe
            config (Config, optional): Config to be used. Defaults to None.
        """

        self._dfs = dfs

        if config:
            self.load_config(config)

        if logger:
            self._logger = logger
        else:
            self._logger = Logger(
                save_logs=self._config.save_logs, verbose=self._config.verbose
            )

        if self._config.middlewares is not None:
            self.add_middlewares(*self._config.middlewares)

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
        self._middlewares.extend(middlewares)

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

    def get_dfs_data_for_prompt(self):
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

    def query(self, query: str):
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
                dfs = self.get_dfs_data_for_prompt()

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

            for middleware in self._middlewares:
                code = middleware(code)

            results = self.execute_code(
                code,
                use_error_correction_framework=self._config.use_error_correction_framework,
            )
            self.last_result = results
            self._logger.log(f"Answer: {results}")

            if len(results) > 1:
                output = results[1]

                if self._config.conversational_answer:
                    # TODO: remove the conversational answer from the result as it is
                    # not needed anymore
                    output = self.conversational_answer(query, output["result"])
                    self._logger.log(f"Conversational answer: {output}")

                self._logger.log(f"Executed in: {time.time() - self._start_time}s")

                if output["type"] == "dataframe":
                    from ..smart_dataframe import SmartDataframe

                    return SmartDataframe(
                        output["result"], config=self._config.__dict__
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
        except Exception as exception:
            self.last_error = str(exception)
            print(exception)
            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def conversational_answer(self, question: str, answer: str) -> str:
        """
        Returns the answer in conversational form about the resultant data.

        Args:
            question (str): A question in Conversational form
            answer (str): A summary / resultant Data

        Returns (str): Response

        """

        if self._config.enforce_privacy:
            # we don't want to send potentially sensitive data to the LLM server
            # if the user has set enforce_privacy to True
            return answer

        generate_response_instruction = self._config.custom_prompts.get(
            "generate_response", GenerateResponsePrompt
        )(question=question, answer=answer)
        return self._llm.call(generate_response_instruction, "")

    def execute_code(
        self,
        code: str,
        use_error_correction_framework: bool = True,
    ) -> str:
        """
        Execute the python code generated by LLMs to answer the question
        about the input dataframe. Run the code in the current context and return the
        result.

        Args:
            code (str): Python code to execute
            data_frame (pd.DataFrame): Full Pandas DataFrame
            use_error_correction_framework (bool): Turn on Error Correction mechanism.
            Default to True

        Returns:
            result: The result of the code execution. The type of the result depends
            on the generated code.

        """

        # Add save chart code
        if self._config.save_charts:
            code = add_save_chart(
                code,
                self._last_prompt_id,
                self._config.save_charts_path,
                not self._config.verbose,
            )

        # Get the code to run removing unsafe imports and df overwrites
        code_to_run = self._clean_code(code)
        self.last_code_executed = code_to_run
        self._logger.log(
            f"""
Code running:
```
{code_to_run}
        ```"""
        )

        environment: dict = self._get_environment()
        count = 0
        while count < self._config.max_retries:
            try:
                # Execute the code
                exec(code_to_run, environment)
                code = code_to_run
                break
            except Exception as e:
                if not use_error_correction_framework:
                    raise e

                count += 1

                code_to_run = self._retry_run_code(code, e)

        result = environment.get("result", None)

        return result

    def _get_environment(self) -> dict:
        """
        Returns the environment for the code to be executed.

        Returns (dict): A dictionary of environment variables
        """

        dfs = []
        for df in self._dfs:
            dfs.append(df.original)

        return {
            "pd": pd,
            "dfs": dfs,
            **{
                lib["alias"]: getattr(import_dependency(lib["module"]), lib["name"])
                if hasattr(import_dependency(lib["module"]), lib["name"])
                else import_dependency(lib["module"])
                for lib in self._additional_dependencies
            },
            "__builtins__": {
                **{builtin: __builtins__[builtin] for builtin in WHITELISTED_BUILTINS},
                "__build_class__": __build_class__,
                "__name__": "__main__",
            },
        }

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

    def _clean_code(self, code: str) -> str:
        """
        A method to clean the code to prevent malicious code execution

        Args:
            code(str): A python code

        Returns (str): Returns a Clean Code String

        """

        tree = ast.parse(code)

        new_body = []

        # clear recent optional dependencies
        self._additional_dependencies = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._check_imports(node)
                continue
            if self._is_df_overwrite(node):
                continue
            new_body.append(node)

        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree, pretty_source=lambda x: "".join(x)).strip()

    def _is_df_overwrite(self, node: ast.stmt) -> bool:
        """
        Remove df declarations from the code to prevent malicious code execution.

        Args:
            node (object): ast.stmt

        Returns (bool):

        """

        return (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and re.match(r"df\d{0,2}$", node.targets[0].id)
        )

    def _check_imports(self, node: Union[ast.Import, ast.ImportFrom]):
        """
        Add whitelisted imports to _additional_dependencies.

        Args:
            node (object): ast.Import or ast.ImportFrom

        Raises:
            BadImportError: If the import is not whitelisted

        """
        if isinstance(node, ast.Import):
            module = node.names[0].name
        else:
            module = node.module

        library = module.split(".")[0]

        if library == "pandas":
            return

        if (
            library
            in WHITELISTED_LIBRARIES + self._config.custom_whitelisted_dependencies
        ):
            for alias in node.names:
                self._additional_dependencies.append(
                    {
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname or alias.name,
                    }
                )
            return

        if library not in WHITELISTED_BUILTINS:
            raise BadImportError(library)

    @property
    def last_prompt(self):
        return self._llm.last_prompt
