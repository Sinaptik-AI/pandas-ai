from typing import Optional

from pandasai.ee.agents.judge_agent.pipeline.judge_prompt_generation import (
    JudgePromptGeneration,
)
from pandasai.ee.agents.judge_agent.pipeline.llm_call import LLMCall
from pandasai.helpers.logger import Logger
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.pipelines.judge.judge_pipeline_input import JudgePipelineInput
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class JudgePipeline:
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
                JudgePromptGeneration(),
                LLMCall(),
            ],
        )

    def run(self, input: JudgePipelineInput):
        return self.pipeline.run(input)
