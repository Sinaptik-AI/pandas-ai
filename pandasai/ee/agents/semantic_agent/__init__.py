import json
from typing import List, Optional, Type, Union

import pandas as pd

from pandasai.agent.base import BaseAgent
from pandasai.connectors.base import BaseConnector
from pandasai.connectors.pandas import PandasConnector
from pandasai.constants import PANDASBI_SETUP_MESSAGE
from pandasai.ee.agents.semantic_agent.pipeline.semantic_chat_pipeline import (
    SemanticChatPipeline,
)
from pandasai.ee.agents.semantic_agent.prompts.generate_df_schema import (
    GenerateDFSchemaPrompt,
)
from pandasai.exceptions import InvalidConfigError
from pandasai.helpers.cache import Cache
from pandasai.helpers.memory import Memory
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.schemas.df_config import Config
from pandasai.vectorstores.vectorstore import VectorStore


class SemanticAgent(BaseAgent):
    """
    Answer Semantic queries
    """

    def __init__(
        self,
        dfs: Union[
            pd.DataFrame, BaseConnector, List[Union[pd.DataFrame, BaseConnector]]
        ],
        config: Optional[Union[Config, dict]] = None,
        memory_size: Optional[int] = 10,
        pipeline: Optional[Type[GenerateChatPipeline]] = None,
        vectorstore: Optional[VectorStore] = None,
        description: str = None,
    ):
        super().__init__(dfs, config, memory_size, vectorstore, description)

        self._validate_config()

        self._schema_cache = Cache("schema")
        self._schema = None

        self._create_schema()

        self.init_duckdb_instance()

        # visualization agent works only with direct sql true
        self.config.direct_sql = True

        self.context = PipelineContext(
            dfs=self.dfs,
            config=self.config,
            memory=Memory(memory_size, agent_info=description),
            vectorstore=self._vectorstore,
            initial_values={"df_schema": self._schema},
        )

        self.pipeline = (
            pipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
            )
            if pipeline
            else SemanticChatPipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
            )
        )

    def init_duckdb_instance(self):
        schema_json = json.loads(self._schema)
        for index, tables in enumerate(schema_json):
            if isinstance(self.dfs[index], PandasConnector):
                self.dfs[index].enable_sql_query(tables["table"])

    def _create_schema(self):
        """
        Generate schema on the initialization of Agent class
        """
        key = self._get_schema_cache_key()
        value = self._schema_cache.get(key)
        if value is not None:
            self._schema = value
            self.logger.log(f"using schema: {self._schema}")
            return

        prompt = GenerateDFSchemaPrompt(context=self.context)

        result = self.call_llm_with_prompt(prompt)
        self.logger.log(
            f"""Initializing Schema:  {result}
            """
        )
        self._schema = result.replace("# SAMPLE SCHEMA", "")
        # save schema in the cache
        self._schema_cache.set(key, self._schema)
        self.logger.log(f"using schema: {self._schema}")

    def _validate_config(self):
        if not isinstance(self.config.llm, BambooLLM):
            raise InvalidConfigError(
                f"""Visualization Agent works only with BambooLLM follow instructions for setup:\n {PANDASBI_SETUP_MESSAGE}"""
            )

    def _get_schema_cache_key(self):
        """
        Generate schema key
        Returns:
            str: key of schema stored in db
        """
        return "".join(str(df.column_hash) for df in self.context.dfs)

    @property
    def last_error(self):
        return self.pipeline.last_error

    @property
    def last_query_log_id(self):
        return self.pipeline.get_last_track_log_id()
