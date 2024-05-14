from typing import Optional

from pandasai.ee.agents.visualization_agent.pipeline.llm_call import LLMCall
from pandasai.ee.agents.visualization_agent.pipeline.viz_prompt_generation import (
    VizPromptGeneration,
)
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline import (
    ErrorCorrectionPipeline,
)
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline

# from .validate_pipeline_input import ValidatePipelineInput

from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline import Pipeline

# from pandasai.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.chat.cache_lookup import CacheLookup

# from pandasai.pipelines.chat.cache_population import CachePopulation
# from pandasai.pipelines.chat.code_cleaning import CodeCleaning
# from pandasai.pipelines.chat.code_execution import CodeExecution
# from pandasai.pipelines.chat.code_generator import CodeGenerator
# from pandasai.pipelines.chat.prompt_generation import PromptGeneration
# from pandasai.pipelines.chat.result_parsing import ResultParsing
# from pandasai.pipelines.chat.result_validation import ResultValidation


class VisualizationChatPipeline(GenerateChatPipeline):
    code_generation_pipeline = Pipeline
    code_execution_pipeline = Pipeline
    context: PipelineContext
    _logger: Logger
    last_error: str

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        on_prompt_generation=None,
        on_code_generation=None,
        before_code_execution=None,
        on_result=None,
    ):
        super().__init__(context, logger)

        self.code_generation_pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            steps=[
                # ValidatePipelineInput(),
                CacheLookup(),
                VizPromptGeneration(
                    skip_if=self.is_cached,
                    on_execution=on_prompt_generation,
                ),
                LLMCall(),
                # CodeGenerator(
                #     skip_if=self.is_cached,
                #     on_execution=on_code_generation,
                # ),
                # CachePopulation(skip_if=self.is_cached),
                # CodeCleaning(
                #     skip_if=self.no_code,
                #     on_failure=self.on_code_cleaning_failure,
                #     on_retry=self.on_code_retry,
                # ),
            ],
        )

        self.code_execution_pipeline = None

        # self.code_execution_pipeline = Pipeline(
        #     context=context,
        #     logger=logger,
        #     query_exec_tracker=self.query_exec_tracker,
        #     steps=[
        #         CodeExecution(
        #             before_execution=before_code_execution,
        #             on_failure=self.on_code_execution_failure,
        #             on_retry=self.on_code_retry,
        #         ),
        #         ResultValidation(),
        #         ResultParsing(
        #             before_execution=on_result,
        #         ),
        #     ],
        # )

        self.code_exec_error_pipeline = ErrorCorrectionPipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self.context = context
        self._logger = logger
        self.last_error = None
