import json
from typing import Any

from pandasai.ee.agents.semantic_agent.prompts.semantic_agent_prompt import (
    SemanticAgentPrompt,
)
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext


class SemanticPromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method will return output according to
        Implementation.

        :param input: Last logic unit output
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: LogicUnitOutput(prompt)
        """
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        prompt = SemanticAgentPrompt(
            context=self.context, schema=json.dumps(self.context.get("df_schema"))
        )
        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {"content_type": "prompt", "value": prompt.to_string()},
        )
