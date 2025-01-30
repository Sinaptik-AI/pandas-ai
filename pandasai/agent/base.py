import traceback
import warnings
from typing import Any, List, Optional, Union

import duckdb
import pandas as pd

from pandasai.core.cache import Cache
from pandasai.core.code_execution.code_executor import CodeExecutor
from pandasai.core.code_generation.base import CodeGenerator
from pandasai.core.prompts import (
    get_chat_prompt_for_sql,
    get_correct_error_prompt_for_sql,
    get_correct_output_type_error_prompt,
)
from pandasai.core.response.error import ErrorResponse
from pandasai.core.response.parser import ResponseParser
from pandasai.core.user_query import UserQuery
from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import (
    CodeExecutionError,
    InvalidLLMOutputType,
    MissingVectorStoreError,
)
from pandasai.sandbox import Sandbox
from pandasai.vectorstores.vectorstore import VectorStore

from ..config import Config
from ..constants import LOCAL_SOURCE_TYPES
from .state import AgentState


class Agent:
    """
    Base Agent class to improve the conversational experience in PandaAI
    """

    def __init__(
        self,
        dfs: Union[
            Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]
        ],
        config: Optional[Union[Config, dict]] = None,
        memory_size: Optional[int] = 10,
        vectorstore: Optional[VectorStore] = None,
        description: str = None,
        sandbox: Sandbox = None,
    ):
        """
        Args:
            dfs (Union[Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]]): The dataframe(s) to be used for the conversation.
            config (Optional[Union[Config, dict]]): The configuration for the agent.
            memory_size (Optional[int]): The size of the memory.
            vectorstore (Optional[VectorStore]): The vectorstore to be used for the conversation.
            description (str): The description of the agent.
        """

        # Deprecation warnings
        if config is not None:
            warnings.warn(
                "The 'config' parameter is deprecated and will be removed in a future version. "
                "Please use the global configuration instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        self.description = description
        self._state = AgentState()
        self._state.initialize(dfs, config, memory_size, vectorstore, description)

        self._code_generator = CodeGenerator(self._state)
        self._response_parser = ResponseParser()
        self._sandbox = sandbox

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Start a new chat interaction with the assistant on Dataframe.
        """
        self.start_new_conversation()
        return self._process_query(query, output_type)

    def follow_up(self, query: str, output_type: Optional[str] = None):
        """
        Continue the existing chat interaction with the assistant on Dataframe.
        """
        return self._process_query(query, output_type)

    def generate_code(self, query: Union[UserQuery, str]) -> str:
        """Generate code using the LLM."""

        self._state.memory.add(str(query), is_user=True)
        if self._state.config.enable_cache:
            cached_code = self._state.cache.get(
                self._state.cache.get_cache_key(self._state)
            )
            if cached_code:
                self._state.logger.log("Using cached code.")
                return self._code_generator.validate_and_clean_code(cached_code)

        self._state.logger.log("Generating new code...")
        prompt = get_chat_prompt_for_sql(self._state)

        code = self._code_generator.generate_code(prompt)
        self._state.last_prompt_used = prompt
        return code

    def execute_code(self, code: str) -> dict:
        """Execute the generated code."""
        self._state.logger.log(f"Executing code: {code}")

        code_executor = CodeExecutor(self._state.config)
        code_executor.add_to_env("execute_sql_query", self._execute_sql_query)

        if self._sandbox:
            return self._sandbox.execute(code, code_executor.environment)

        return code_executor.execute_and_return_result(code)

    def _execute_local_sql_query(self, query: str) -> pd.DataFrame:
        try:
            # Use a context manager to ensure the connection is closed
            with duckdb.connect() as con:
                # Register all DataFrames in the state
                for df in self._state.dfs:
                    con.register(df.schema.source.table, df)

                # Execute the query and fetch the result as a pandas DataFrame
                result = con.sql(query).df()

            return result
        except duckdb.Error as e:
            raise RuntimeError(f"SQL execution failed: {e}") from e

    def _execute_sql_query(self, query: str) -> pd.DataFrame:
        """
        Executes an SQL query on registered DataFrames.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the SQL query as a pandas DataFrame.
        """
        if not self._state.dfs:
            raise ValueError("No DataFrames available to register for query execution.")

        if self._state.dfs[0].schema.source.type in LOCAL_SOURCE_TYPES:
            return self._execute_local_sql_query(query)
        else:
            return self._state.dfs[0].execute_sql_query(query)

    def execute_with_retries(self, code: str) -> Any:
        """Execute the code with retry logic."""
        max_retries = self._state.config.max_retries
        attempts = 0

        while attempts <= max_retries:
            try:
                result = self.execute_code(code)
                return self._response_parser.parse(result, code)
            except CodeExecutionError as e:
                attempts += 1
                if attempts > max_retries:
                    self._state.logger.log(f"Max retries reached. Error: {e}")
                    raise
                self._state.logger.log(
                    f"Retrying execution ({attempts}/{max_retries})..."
                )
                code = self._regenerate_code_after_error(code, e)

    def train(
        self,
        queries: Optional[List[str]] = None,
        codes: Optional[List[str]] = None,
        docs: Optional[List[str]] = None,
    ) -> None:
        """
        Trains the context to be passed to model
        Args:
            queries (Optional[str], optional): user user
            codes (Optional[str], optional): generated code
            docs (Optional[List[str]], optional): additional docs
        Raises:
            ImportError: if default vector db lib is not installed it raises an error
        """
        if self._state.vectorstore is None:
            raise MissingVectorStoreError(
                "No vector store provided. Please provide a vector store to train the agent."
            )

        if (queries and not codes) or (not queries and codes):
            raise ValueError(
                "If either queries or codes are provided, both must be provided."
            )

        if docs is not None:
            self._state.vectorstore.add_docs(docs)

        if queries and codes:
            self._state.vectorstore.add_question_answer(queries, codes)

        self._state.logger.log("Agent successfully trained on the data")

    def clear_memory(self):
        """
        Clears the memory
        """
        self._state.memory.clear()

    def add_message(self, message, is_user=False):
        """
        Add message to the memory. This is useful when you want to add a message
        to the memory without calling the chat function (for example, when you
        need to add a message from the agent).
        """
        self._state.memory.add(message, is_user=is_user)

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self.clear_memory()

    def _process_query(self, query: str, output_type: Optional[str] = None):
        """Process a user query and return the result."""
        query = UserQuery(query)
        self._state.logger.log(f"Question: {query}")
        self._state.logger.log(
            f"Running PandaAI with {self._state.config.llm.type} LLM..."
        )

        self._state.output_type = output_type
        try:
            self._state.assign_prompt_id()

            # To ensure the cache is set properly if config is changed in between
            if self._state.config.enable_cache and self._state.cache is None:
                self._state.cache = Cache()

            # Generate code
            code = self.generate_code(query)

            # Execute code with retries
            result = self.execute_with_retries(code)

            # Cache the result if caching is enabled
            if self._state.config.enable_cache:
                self._state.cache.set(
                    self._state.cache.get_cache_key(self._state), code
                )

            self._state.logger.log("Response generated successfully.")
            # Generate and return the final response
            return result

        except CodeExecutionError:
            return self._handle_exception(code)

    def _regenerate_code_after_error(self, code: str, error: Exception) -> str:
        """Generate a new code snippet based on the error."""
        error_trace = traceback.format_exc()
        self._state.logger.log(f"Execution failed with error: {error_trace}")

        if isinstance(error, InvalidLLMOutputType):
            prompt = get_correct_output_type_error_prompt(
                self._state, code, error_trace
            )
        else:
            prompt = get_correct_error_prompt_for_sql(self._state, code, error_trace)

        return self._code_generator.generate_code(prompt)

    def _handle_exception(self, code: str) -> str:
        """Handle exceptions and return an error message."""
        error_message = traceback.format_exc()
        self._state.logger.log(f"Processing failed with error: {error_message}")

        return ErrorResponse(last_code_executed=code, error=error_message)

    @property
    def last_generated_code(self):
        return self._state.last_code_generated

    @property
    def last_code_executed(self):
        return self._state.last_code_generated

    @property
    def last_prompt_used(self):
        return self._state.last_prompt_used
