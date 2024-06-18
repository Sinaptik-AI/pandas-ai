import json
from typing import List, Optional, Type, Union

import pandas as pd

from pandasai.agent.base import BaseAgent
from pandasai.agent.base_judge import BaseJudge
from pandasai.connectors.base import BaseConnector
from pandasai.connectors.pandas import PandasConnector
from pandasai.constants import PANDASBI_SETUP_MESSAGE
from pandasai.ee.agents.semantic_agent.pipeline.code_generator import CodeGenerator
from pandasai.ee.agents.semantic_agent.pipeline.semantic_chat_pipeline import (
    SemanticChatPipeline,
)
from pandasai.ee.agents.semantic_agent.prompts.generate_df_schema import (
    GenerateDFSchemaPrompt,
)
from pandasai.exceptions import InvalidConfigError, InvalidSchemaJson, InvalidTrainJson
from pandasai.helpers.cache import Cache
from pandasai.helpers.memory import Memory
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.pipelines.pipeline import Pipeline
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
        schema: Optional[List[dict]] = None,
        memory_size: Optional[int] = 10,
        pipeline: Optional[Type[GenerateChatPipeline]] = None,
        vectorstore: Optional[VectorStore] = None,
        description: str = None,
        judge: BaseJudge = None,
    ):
        super().__init__(dfs, config, memory_size, vectorstore, description)

        self._validate_config()

        self._schema_cache = Cache("schema")
        self._schema = schema or None

        self._create_schema()

        self._sort_dfs_according_to_schema()

        self.init_duckdb_instance()

        # semantic agent works only with direct sql true
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
                judge=judge,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
            )
            if pipeline
            else SemanticChatPipeline(
                self.context,
                self.logger,
                judge=judge,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
            )
        )

    def validate_and_convert_json(self, jsons):
        json_strs = []

        try:
            for json_data in jsons:
                if isinstance(json_data, str):
                    json.loads(json_data)
                    json_strs.append(json_data)
                elif isinstance(json_data, dict):
                    json_strs.append(json.dumps(json_data))

        except Exception as e:
            raise InvalidTrainJson("Error validating JSON string") from e

        return json_strs

    def train(
        self,
        queries: Optional[List[str]] = None,
        jsons: Optional[List[Union[dict, str]]] = None,
        docs: Optional[List[str]] = None,
    ) -> None:
        json_strs = self.validate_and_convert_json(jsons) if jsons else None

        super().train(queries=queries, codes=json_strs, docs=docs)

    def query(self, query):
        query_pipeline = Pipeline(
            context=self.context,
            logger=self.logger,
            steps=[
                CodeGenerator(),
            ],
        )
        code = query_pipeline.run(query)

        self.execute_code(code)

    def init_duckdb_instance(self):
        for index, tables in enumerate(self._schema):
            if isinstance(self.dfs[index], PandasConnector):
                self._sync_pandas_dataframe_schema(self.dfs[index], tables)
                self.dfs[index].enable_sql_query(tables["table"])

    def _sync_pandas_dataframe_schema(self, df: PandasConnector, schema: dict):
        for dimension in schema["dimensions"]:
            if dimension["type"] in ["date", "datetime", "timestamp"]:
                column = dimension["sql"]
                df.pandas_df[column] = pd.to_datetime(df.pandas_df[column])

    def _sort_dfs_according_to_schema(self):
        schema_dict = {
            table["table"]: [dim["sql"] for dim in table["dimensions"]]
            for table in self._schema
        }
        sorted_dfs = []

        for table in self._schema:
            matched = False
            for df in self.dfs:
                df_columns = df.get_head().columns
                if all(column in df_columns for column in schema_dict[table["table"]]):
                    sorted_dfs.append(df)
                    matched = True

            if not matched:
                raise InvalidSchemaJson(
                    f"Some sql column of table {table['table']} doesn't match with any dataframe"
                )

        self.dfs = sorted_dfs

    def _create_schema(self):
        """
        Generate schema on the initialization of Agent class
        """
        if self._schema:
            self.logger.log(f"using user provided schema: {self._schema}")
            return

        key = self._get_schema_cache_key()
        if self.config.enable_cache:
            value = self._schema_cache.get(key)
            if value is not None:
                self._schema = json.loads(value)
                self.logger.log(f"using schema: {self._schema}")
                return

        prompt = GenerateDFSchemaPrompt(context=self.context)

        result = self.call_llm_with_prompt(prompt)
        self.logger.log(
            f"""Initializing Schema:  {result}
            """
        )
        self._schema = result.replace("# SAMPLE SCHEMA", "")
        schema_data = json.loads(result.replace("# SAMPLE SCHEMA", ""))
        if isinstance(schema_data, dict):
            schema_data = [schema_data]

        self._schema = schema_data
        # save schema in the cache
        if self.config.enable_cache:
            self._schema_cache.set(key, json.dumps(self._schema))

        self.logger.log(f"using schema: {self._schema}")

    def _validate_config(self):
        if not isinstance(self.config.llm, BambooLLM):
            raise InvalidConfigError(
                f"""Semantic Agent works only with BambooLLM follow instructions for setup:\n {PANDASBI_SETUP_MESSAGE}"""
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
