from typing import Optional
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
    _pipeline: Pipeline

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self._pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                CacheLookup(),
                PromptGeneration(
                    skip_if=lambda pipeline_context: pipeline_context.get_intermediate_value(
                        "is_present_in_cache"
                    )
                ),
                CodeGenerator(
                    skip_if=lambda pipeline_context: pipeline_context.get_intermediate_value(
                        "is_present_in_cache"
                    )
                ),
                CachePopulation(
                    skip_if=lambda pipeline_context: pipeline_context.get_intermediate_value(
                        "is_present_in_cache"
                    )
                ),
                CodeExecution(),
                ResultValidation(),
                ResultParsing(),
            ],
        )

    def run(self):
        return self._pipeline.run()
