from typing import Optional

from pandasai.ee.agents.semantic_agent.pipeline.code_generator import CodeGenerator
from pandasai.ee.agents.semantic_agent.pipeline.error_correction_pipeline.fix_semantic_json_pipeline import (
    FixSemanticJsonPipeline,
)
from pandasai.ee.agents.semantic_agent.pipeline.llm_call import LLMCall
from pandasai.ee.agents.semantic_agent.pipeline.Semantic_prompt_generation import (
    SemanticPromptGeneration,
)
from pandasai.helpers.logger import Logger
from pandasai.pipelines.chat.code_cleaning import CodeCleaning
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class ErrorCorrectionPipeline:
    """
    Error Correction Pipeline to regenerate prompt and code
    """

    _context: PipelineContext
    _logger: Logger

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        on_prompt_generation=None,
        on_code_generation=None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                SemanticPromptGeneration(
                    on_execution=on_prompt_generation,
                ),
                LLMCall(),
                CodeGenerator(
                    on_execution=on_code_generation,
                    on_failure=self.on_wrong_semantic_json,
                ),
                CodeCleaning(),
            ],
        )

        self.fix_semantic_json_pipeline = FixSemanticJsonPipeline(
            context=context,
            logger=logger,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self._context = context
        self._logger = logger

    def run(self, input: ErrorCorrectionPipelineInput):
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")
        return self.pipeline.run(input)

    def on_wrong_semantic_json(self, code, errors):
        correction_input = ErrorCorrectionPipelineInput(code, errors)
        return self.fix_semantic_json_pipeline.run(correction_input)
