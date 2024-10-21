from typing import Optional

from pandasai.ee.agents.judge_agent.pipeline.judge_prompt_generation import (
    JudgePromptGeneration,
)
from pandasai.ee.agents.judge_agent.pipeline.llm_call import LLMCall
from pandasai.helpers.logger import Logger
from pandasai.pipelines.judge.judge_pipeline_input import JudgePipelineInput
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class JudgePipeline:
    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                JudgePromptGeneration(),
                LLMCall(),
            ],
        )

    def run(self, input: JudgePipelineInput):
        return self.pipeline.run(input)
