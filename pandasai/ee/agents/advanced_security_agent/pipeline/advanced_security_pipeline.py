from typing import Optional

from pandasai.ee.agents.advanced_security_agent.pipeline.advanced_security_prompt_generation import (
    AdvancedSecurityPromptGeneration,
)
from pandasai.ee.agents.judge_agent.pipeline.llm_call import LLMCall
from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class AdvancedSecurityPipeline:
    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                AdvancedSecurityPromptGeneration(),
                LLMCall(),
            ],
        )

    def run(self, input: str):
        return self.pipeline.run(input)
