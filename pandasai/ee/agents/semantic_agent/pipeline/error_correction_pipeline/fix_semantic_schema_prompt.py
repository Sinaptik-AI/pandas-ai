import json
from typing import Any, Callable

from pandasai.ee.agents.semantic_agent.prompts.fix_semantic_json import (
    FixSemanticJsonPrompt,
)
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext


class FixSemanticSchemaPrompt(BaseLogicUnit):
    on_prompt_generation: Callable[[str], None]

    def __init__(
        self,
        on_prompt_generation=None,
        skip_if=None,
        on_execution=None,
        before_execution=None,
    ):
        self.on_prompt_generation = on_prompt_generation
        super().__init__(skip_if, on_execution, before_execution)

    def execute(self, input: ErrorCorrectionPipelineInput, **kwargs) -> Any:
        """
        A method to retry the code execution with error correction framework.

        Args:
            code (str): A python code
            context (PipelineContext) : Pipeline Context
            logger (Logger) : Logger
            e (Exception): An exception
            dataframes

        Returns (str): A python code
        """
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        prompt = FixSemanticJsonPrompt(
            context=self.context,
            generated_json=input.code,
            error=input.exception,
            schema=json.dumps(self.context.get("df_schema")),
        )
        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {
                "content_type": "prompt",
                "value": prompt.to_string(),
            },
        )
