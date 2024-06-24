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
from pandasai.helpers.query_exec_tracker import QueryExecTracker
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
        query_exec_tracker: QueryExecTracker = None,
        on_prompt_generation=None,
        on_code_generation=None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=query_exec_tracker,
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
            query_exec_tracker=query_exec_tracker,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )
        self.query_exec_tracker = query_exec_tracker

        self._context = context
        self._logger = logger

    def run(self, input: ErrorCorrectionPipelineInput):
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")
        return self.pipeline.run(input)

    def on_wrong_semantic_json(self, code, errors):
        self.query_exec_tracker.add_step(
            {
                "type": "CodeGenerator",
                "success": False,
                "message": "Failed to validate json",
                "execution_time": None,
                "data": {
                    "content_type": "code",
                    "value": code,
                    "exception": errors,
                },
            }
        )
        correction_input = ErrorCorrectionPipelineInput(code, errors)
        return self.fix_semantic_json_pipeline.run(correction_input)
