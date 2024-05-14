from typing import List, Optional, Type, Union

import pandas as pd
from pandasai.agent.base import BaseAgent
from pandasai.connectors.base import BaseConnector
from pandasai.pipelines.chat.chat_pipeline_input import ChatPipelineInput
from pandasai.pipelines.chat.code_execution_pipeline_input import (
    CodeExecutionPipelineInput,
)
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.schemas.df_config import Config
from pandasai.vectorstores.vectorstore import VectorStore


class Agent(BaseAgent):
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
            else GenerateChatPipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
            )
        )

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Simulate a chat interaction with the assistant on Dataframe.
        """
        try:
            self.logger.log(f"Question: {query}")
            self.logger.log(
                f"Running PandasAI with {self.context.config.llm.type} LLM..."
            )

            self.assign_prompt_id()

            pipeline_input = ChatPipelineInput(
                query, output_type, self.conversation_id, self.last_prompt_id
            )

            return self.pipeline.run(pipeline_input)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def generate_code(self, query: str, output_type: Optional[str] = None):
        """
        Simulate code generation with the assistant on Dataframe.
        """
        try:
            self.logger.log(f"Question: {query}")
            self.logger.log(
                f"Running PandasAI with {self.context.config.llm.type} LLM..."
            )

            self.assign_prompt_id()

            pipeline_input = ChatPipelineInput(
                query, output_type, self.conversation_id, self.last_prompt_id
            )

            return self.pipeline.run_generate_code(pipeline_input)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def execute_code(
        self, code: Optional[str] = None, output_type: Optional[str] = None
    ):
        """
        Execute code Generated with the assistant on Dataframe.
        """
        try:
            if code is None:
                code = self.last_code_generated
            self.logger.log(f"Code: {code}")
            self.logger.log(
                f"Running PandasAI with {self.context.config.llm.type} LLM..."
            )

            self.assign_prompt_id()

            pipeline_input = CodeExecutionPipelineInput(
                code, output_type, self.conversation_id, self.last_prompt_id
            )

            return self.pipeline.run_execute_code(pipeline_input)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    @property
    def last_error(self):
        return self.pipeline.last_error

    @property
    def last_query_log_id(self):
        return self.pipeline.get_last_track_log_id()
