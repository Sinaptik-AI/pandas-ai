from typing import List, Optional, Type, Union

import pandas as pd

from pandasai.agent.base import BaseAgent
from pandasai.agent.base_judge import BaseJudge
from pandasai.agent.base_security import BaseSecurity
from pandasai.connectors.base import BaseConnector
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
        judge: BaseJudge = None,
        security: BaseSecurity = None,
        check_query_malicious: bool = True,
        do_regex_search_code_cleaning: bool = True,
    ):
        super().__init__(
            dfs,
            config,
            memory_size,
            vectorstore,
            description,
            security=security,
            check_query_malicious=check_query_malicious,
        )

        self.pipeline = (
            pipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
                judge=judge,
            )
            if pipeline
            else GenerateChatPipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
                do_regex_search_code_cleaning=do_regex_search_code_cleaning,
                judge=judge,
            )
        )

    @property
    def last_error(self):
        return self.pipeline.last_error

    @property
    def last_query_log_id(self):
        return self.pipeline.get_last_track_log_id()
