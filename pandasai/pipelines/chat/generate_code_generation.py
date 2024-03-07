from typing import Optional

from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.pipelines.chat.cache_lookup import CacheLookup
from pandasai.pipelines.chat.cache_population import CachePopulation
from pandasai.pipelines.chat.chat_pipeline_input import ChatPipelineInput
from pandasai.pipelines.chat.code_generator import CodeGenerator
from pandasai.pipelines.chat.generate_code_execution import (
    GenerateCodeExecutionPipeline,
)
from pandasai.pipelines.chat.prompt_generation import PromptGeneration
from pandasai.pipelines.chat.validate_pipeline_input import ValidatePipelineInput

from ...helpers.logger import Logger
from ..pipeline import Pipeline
from ..pipeline_context import PipelineContext


class GenerateCodeGenerationPipeline:
    pipeline: Pipeline
    context: PipelineContext
    _logger: Logger

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        on_prompt_generation=None,
        on_code_generation=None,
    ):
        self.query_exec_tracker = QueryExecTracker(
            server_config=context.config.log_server
        )

        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=self.query_exec_tracker,
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
            ],
        )

        self.context = context
        self._logger = logger

    def is_cached(self, context: PipelineContext):
        return context.get("found_in_cache")

    def get_last_track_log_id(self):
        return self.query_exec_tracker.last_log_id

    def run(self, input: ChatPipelineInput) -> dict:
        """
        Executes the chat pipeline with user input and return the result
        Args:
            input (ChatPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.
        """
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

        # Reset intermediate values
        self.context.reset_intermediate_values()

        # Start New Tracking for Query
        self.query_exec_tracker.start_new_track(input)

        self.query_exec_tracker.add_skills(self.context)

        self.query_exec_tracker.add_dataframes(self.context.dfs)

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            output = self.pipeline.run(input)

            self.query_exec_tracker.success = True

            self.query_exec_tracker.publish()

            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)
            self.query_exec_tracker.success = False
            self.query_exec_tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )

    def pipe(
        self, pipeline2: GenerateCodeExecutionPipeline, input: ChatPipelineInput
    ) -> dict:
        """
        Pipe pipeline execution
        Args:
            pipeline2(GenerateCodeExecutionPipeline): Pipeline to be piped after the self
            input (ChatPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.
        """
        try:
            self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

            # Reset intermediate values
            self.context.reset_intermediate_values()

            # Start New Tracking for Query
            self.query_exec_tracker.start_new_track(input)

            self.query_exec_tracker.add_skills(self.context)

            self.query_exec_tracker.add_dataframes(self.context.dfs)

            # Add Query to memory
            self.context.memory.add(input.query, True)

            self.context.add_many(
                {
                    "output_type": input.output_type,
                    "last_prompt_id": input.prompt_id,
                }
            )

            pipeline2.query_exec_tracker.start_new_track(input)
            output = self.pipeline.pipe(pipeline2.pipeline)
            self.query_exec_tracker.success = True
            pipeline2.query_exec_tracker.success = True
            pipeline2.query_exec_tracker.publish()
            self.query_exec_tracker.publish()
            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)
            self.query_exec_tracker.success = False
            self.query_exec_tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )
