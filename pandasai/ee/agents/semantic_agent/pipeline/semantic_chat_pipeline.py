from typing import Optional

from pandasai.agent.base_judge import BaseJudge
from pandasai.ee.agents.semantic_agent.pipeline.code_generator import CodeGenerator
from pandasai.ee.agents.semantic_agent.pipeline.error_correction_pipeline.error_correction_pipeline import (
    ErrorCorrectionPipeline,
)
from pandasai.ee.agents.semantic_agent.pipeline.error_correction_pipeline.fix_semantic_json_pipeline import (
    FixSemanticJsonPipeline,
)
from pandasai.ee.agents.semantic_agent.pipeline.llm_call import LLMCall
from pandasai.ee.agents.semantic_agent.pipeline.Semantic_prompt_generation import (
    SemanticPromptGeneration,
)
from pandasai.ee.agents.semantic_agent.pipeline.semantic_result_parsing import (
    SemanticResultParser,
)
from pandasai.ee.agents.semantic_agent.pipeline.validate_pipeline_input import (
    ValidatePipelineInput,
)
from pandasai.helpers.logger import Logger
from pandasai.pipelines.chat.cache_lookup import CacheLookup
from pandasai.pipelines.chat.code_cleaning import CodeCleaning
from pandasai.pipelines.chat.code_execution import CodeExecution
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.pipelines.chat.result_validation import ResultValidation
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class SemanticChatPipeline(GenerateChatPipeline):
    code_generation_pipeline = Pipeline
    code_execution_pipeline = Pipeline
    context: PipelineContext
    _logger: Logger
    last_error: str

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        judge: BaseJudge = None,
        on_prompt_generation=None,
        on_code_generation=None,
        before_code_execution=None,
        on_result=None,
    ):
        super().__init__(
            context,
            logger,
            judge=judge,
            on_prompt_generation=on_prompt_generation,
            on_code_generation=on_code_generation,
            before_code_execution=before_code_execution,
            on_result=on_result,
        )

        self.code_generation_pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            steps=[
                ValidatePipelineInput(),
                CacheLookup(),
                SemanticPromptGeneration(
                    skip_if=self.is_cached,
                    on_execution=on_prompt_generation,
                ),
                LLMCall(),
                CodeGenerator(
                    on_execution=on_code_generation,
                    on_failure=self.on_wrong_semantic_json,
                ),
                CodeCleaning(
                    skip_if=self.no_code,
                    on_failure=self.on_code_cleaning_failure,
                    on_retry=self.on_code_retry,
                ),
            ],
        )

        self.code_execution_pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            steps=[
                CodeExecution(
                    before_execution=before_code_execution,
                    on_failure=self.on_code_execution_failure,
                    on_retry=self.on_code_retry,
                ),
                ResultValidation(),
                SemanticResultParser(
                    before_execution=on_result,
                ),
            ],
        )

        self.code_exec_error_pipeline = ErrorCorrectionPipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self.fix_semantic_json_pipeline = FixSemanticJsonPipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self.context = context
        self._logger = logger
        self.last_error = None

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
