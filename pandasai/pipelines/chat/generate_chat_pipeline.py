from typing import Optional

from pandasai.agent.base_judge import BaseJudge
from pandasai.pipelines.chat.chat_pipeline_input import (
    ChatPipelineInput,
)
from pandasai.pipelines.chat.code_execution_pipeline_input import (
    CodeExecutionPipelineInput,
)
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline import (
    ErrorCorrectionPipeline,
)
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.chat.validate_pipeline_input import (
    ValidatePipelineInput,
)

from ...helpers.logger import Logger
from ..pipeline import Pipeline
from ..pipeline_context import PipelineContext
from .cache_lookup import CacheLookup
from .cache_population import CachePopulation
from .code_cleaning import CodeCleaning
from .code_execution import CodeExecution
from .code_generator import CodeGenerator
from .prompt_generation import PromptGeneration
from .result_parsing import ResultParsing
from .result_validation import ResultValidation


class GenerateChatPipeline:
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
        self.code_generation_pipeline = Pipeline(
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
                CodeCleaning(
                    skip_if=self.no_code,
                    on_retry=self.on_code_retry,
                ),
            ],
        )

        self.code_execution_pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                CodeExecution(
                    before_execution=before_code_execution,
                    on_retry=self.on_code_retry,
                ),
                ResultValidation(),
                ResultParsing(
                    before_execution=on_result,
                ),
            ],
        )

        self.code_exec_error_pipeline = ErrorCorrectionPipeline(
            context=context,
            logger=logger,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self.judge = judge

        if self.judge:
            if self.judge.pipeline.pipeline.context:
                self.judge.pipeline.pipeline.context.memory = context.memory
            else:
                self.judge.pipeline.pipeline.context = context

            self.judge.pipeline.pipeline.logger = logger

        self.context = context
        self._logger = logger
        self.last_error = None

    def on_code_retry(self, code: str, exception: Exception):
        correction_input = ErrorCorrectionPipelineInput(code, exception)
        return self.code_exec_error_pipeline.run(correction_input)

    def no_code(self, context: PipelineContext):
        return context.get("last_code_generated") is None

    def is_cached(self, context: PipelineContext):
        return context.get("found_in_cache")

    def run_generate_code(self, input: ChatPipelineInput) -> dict:
        """
        Executes the code generation pipeline with user input and return the result
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

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            return self.code_generation_pipeline.run(input)

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )

    def run_execute_code(self, input: CodeExecutionPipelineInput) -> dict:
        """
        Executes the chat pipeline with user input and return the result
        Args:
            input (CodeExecutionPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.
        """
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

        # Reset intermediate values
        self.context.reset_intermediate_values()

        # Add Query to memory
        self.context.memory.add(input.code, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            return self.code_execution_pipeline.run(input.code)

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )

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

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            if self.judge:
                code = self.code_generation_pipeline.run(input)

                retry_count = 0
                while retry_count < self.context.config.max_retries:
                    if self.judge.evaluate(query=input.query, code=code):
                        break
                    code = self.code_generation_pipeline.run(input)
                    retry_count += 1

                output = self.code_execution_pipeline.run(code)

            elif self.code_execution_pipeline:
                output = (
                    self.code_generation_pipeline | self.code_execution_pipeline
                ).run(input)
            else:
                output = self.code_generation_pipeline.run(input)

            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )
