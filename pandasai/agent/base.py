import os
import traceback
import uuid
import warnings
from importlib.util import find_spec
from typing import Any, List, Optional, Union

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
from pandasai.data_loader.schema_validator import is_schema_source_same
from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.vectorstores.vectorstore import VectorStore

from ..config import Config
from ..constants import DEFAULT_CACHE_DIRECTORY, DEFAULT_CHART_DIRECTORY
from ..exceptions import (
    CodeExecutionError,
    InvalidConfigError,
    InvalidLLMOutputType,
    MissingVectorStoreError,
)
from ..helpers.folder import Folder
from ..helpers.logger import Logger
from ..helpers.memory import Memory
from ..llm.base import LLM
from .state import AgentState


class Agent:
    """
    Base Agent class to improve the conversational experience in PandasAI
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
    ):
        """
        Args:
            df (Union[pd.DataFrame, List[pd.DataFrame]]): Pandas or Modin dataframe or Database connectors
            memory_size (int, optional): Conversation history to use during chat.
            Defaults to 1.
        """
        if config is not None:
            warnings.warn(
                "The 'config' parameter is deprecated and will be removed in a future version. "
                "Please use the global configuration instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        self._state = AgentState()

        self.agent_info = description

        # Instantiate dfs
        self._state.dfs = dfs if isinstance(dfs, list) else [dfs]

        # Instantiate the config
        self._state.config = self._get_config(config)

        # Validate df input with configurations
        self._validate_input()

        # Initialize the context
        self._state.memory = Memory(memory_size, agent_info=description)

        # Instantiate the logger
        self._state.logger = Logger(
            save_logs=self._state.config.save_logs, verbose=self._state.config.verbose
        )

        # If user provided config but not llm but have setup the env for BambooLLM, will be deprecated in future
        if config:
            self._state.config.llm = self._get_llm(self._state.config.llm)

        # Initiate VectorStore
        self._state.vectorstore = vectorstore

        # Initialize Cache
        self._state.cache = Cache() if self._state.config.enable_cache else None

        # Setup directory paths for cache and charts
        self._configure()

        # Initialize Code Generator
        self._code_generator = CodeGenerator(self._state)

        # Initialize Response Generator
        self._response_parser = ResponseParser()

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
        print("+++ code in generate_code: ", code)
        self._state.last_prompt_used = prompt
        return code

    def execute_code(self, code: str) -> dict:
        """Execute the generated code."""
        self._state.logger.log(f"Executing code: {code}")
        code_executor = CodeExecutor(self._state.config)
        code_executor.add_to_env("dfs", self._state.dfs)

        code_executor.add_to_env(
            "execute_sql_query", self._state.dfs[0].execute_sql_query
        )

        return code_executor.execute_and_return_result(code)

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

    def _validate_input(self):
        base_schema_source = self._state.dfs[0].schema
        for df in self._state.dfs[1:]:
            if not is_schema_source_same(base_schema_source, df.schema):
                raise InvalidConfigError(
                    "Direct SQL requires all connectors to be of the same type, "
                    "belong to the same datasource, and have the same credentials."
                )

    def _process_query(self, query: str, output_type: Optional[str] = None):
        """Process a user query and return the result."""
        query = UserQuery(query)
        self._state.logger.log(f"Question: {query}")
        self._state.logger.log(
            f"Running PandasAI with {self._state.config.llm.type} LLM..."
        )

        self._state.output_type = output_type
        try:
            self._assign_prompt_id()

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

    def _configure(self):
        # Add project root path if save_charts_path is default
        if (
            self._state.config.save_charts
            and self._state.config.save_charts_path == DEFAULT_CHART_DIRECTORY
        ):
            Folder.create(self._state.config.save_charts_path)

        # Add project root path if cache_path is default
        if self._state.config.enable_cache:
            Folder.create(DEFAULT_CACHE_DIRECTORY)

    def _get_config(self, config: Union[Config, dict, None]) -> Config:
        """
        Load a config to be used to run the queries.

        Args:
            config (Union[Config, dict]): Config to be used
        """
        if config is None:
            from pandasai.config import ConfigManager

            return ConfigManager.get()

        if isinstance(config, dict):
            if not config.get("llm") and os.environ.get("PANDASAI_API_KEY"):
                config["llm"] = BambooLLM()
            return Config(**config)

        return config

    def _get_llm(self, llm: Optional[LLM] = None) -> LLM:
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

        if llm is None:
            return BambooLLM()

        # Check if pandasai_langchain is installed
        if find_spec("pandasai_langchain") is not None:
            from pandasai_langchain.langchain import LangchainLLM, is_langchain_llm

            if is_langchain_llm(llm):
                llm = LangchainLLM(llm)

        return llm

    def _assign_prompt_id(self):
        """Assign a prompt ID"""

        self._state.last_prompt_id = uuid.uuid4()

        if self._state.logger:
            self._state.logger.log(f"Prompt ID: {self._state.last_prompt_id}")

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
