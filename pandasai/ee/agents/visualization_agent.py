import json
from typing import List, Optional, Type, Union

import pandas as pd
from pandasai.agent.base import BaseAgent
from pandasai.connectors.base import BaseConnector
from pandasai.ee.prompts.generate_visualization_schema import (
    GenerateVisualizationSchemaPrompt,
)
from pandasai.helpers.cache import Cache
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.schemas.df_config import Config
from pandasai.vectorstores.vectorstore import VectorStore


class VisualizationAgent(BaseAgent):
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

        self._schema_cache = Cache("schema")
        self._schema = None

        self.create_schema()

    def _get_schema_cache_key(self):
        return "".join(str(df.column_hash) for df in self.context.dfs)

    def create_schema(self):
        key = self._get_schema_cache_key()
        value = self._schema_cache.get(key)
        if value is not None:
            self._schema = value
            return

        prompt = GenerateVisualizationSchemaPrompt(context=self.context)

        result = self.call_llm_with_prompt(prompt)
        self.logger.log(
            f"""Initializing Schema:  {result}
            """
        )
        result = result.replace("# SAMPLE SCHEMA", "")
        self._schema = json.loads(result)

        # save schema in the cache
        self._schema_cache.set(key, self._schema)
