from typing import Optional

from pandasai.helpers.logger import Logger
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.pipelines.chat.code_generator import CodeGenerator
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.chat.error_correction_pipeline.error_prompt_generation import (
    ErrorPromptGeneration,
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
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=query_exec_tracker,
            steps=[
                ErrorPromptGeneration(on_prompt_generation=on_prompt_generation),
                CodeGenerator(),
            ],
        )
        self._context = context
        self._logger = logger

    def run(self, input: ErrorCorrectionPipelineInput):
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")
        return self.pipeline.run(input)
