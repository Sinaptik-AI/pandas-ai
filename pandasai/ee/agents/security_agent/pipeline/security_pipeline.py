from typing import Optional

from pandasai.ee.agents.judge_agent.pipeline.llm_call import LLMCall
from pandasai.ee.agents.security_agent.pipeline.security_prompt_generation import (
    SecurityPromptGeneration,
)
from pandasai.helpers.logger import Logger
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class SecurityPipeline:
    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        query_exec_tracker: QueryExecTracker = None,
    ):
        self.query_exec_tracker = query_exec_tracker

        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            steps=[
                SecurityPromptGeneration(),
                LLMCall(),
            ],
        )

    def run(self, input: str):
        return self.pipeline.run(input)
