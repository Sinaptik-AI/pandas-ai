from typing import Optional
from pandasai.pipelines.smart_datalake_chat.smart_datalake_pipeline_input import (
    SmartDatalakePipelineInput,
)

from pandasai.pipelines.smart_datalake_chat.validate_pipeline_input import (
    ValidatePipelineInput,
)
from ...helpers.logger import Logger
from ..pipeline import Pipeline
from ..pipeline_context import PipelineContext
from .cache_lookup import CacheLookup
from .cache_population import CachePopulation
from .code_execution import CodeExecution
from .code_generator import CodeGenerator
from .prompt_generation import PromptGeneration
from .result_parsing import ResultParsing
from .result_validation import ResultValidation


class GenerateSmartDatalakePipeline:
    pipeline: Pipeline
    context: PipelineContext

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        on_prompt_generation=None,
        on_code_generation=None,
        on_code_execution=None,
        on_result=None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                ValidatePipelineInput(),
                CacheLookup(),
                PromptGeneration(
                    skip_if=self.is_cached,
                    on_execution=on_prompt_generation,
                ),
                CodeGenerator(
                    skip_if=self.is_cached,
                    on_execution=on_code_generation,
                ),
                CachePopulation(skip_if=self.is_cached),
                CodeExecution(
                    before_execution=on_code_execution,
                    on_failure=on_prompt_generation,
                ),
                ResultValidation(),
                ResultParsing(
                    before_execution=on_result,
                ),
            ],
        )
        self.context = context

    def is_cached(self, context: PipelineContext):
        return context.get("found_in_cache")

    def run(self, input: SmartDatalakePipelineInput) -> dict:
        """
        Executes the smartdatalake pipeline with user input and return the result
        Args:
            input (SmartDatalakePipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.
        """
        # Start New Tracking for Query
        self.context.query_exec_tracker.start_new_track(input)

        self.context.query_exec_tracker.add_dataframes(self.context.dfs)

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type_helper": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )

        return self.pipeline.run()
