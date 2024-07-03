from typing import Any

from pandasai.ee.agents.advanced_security_agent.prompts.advanced_security_agent_prompt import (
    AdvancedSecurityAgentPrompt,
)
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.logic_unit_output import LogicUnitOutput


class AdvancedSecurityPromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

    def execute(self, input_query: str, **kwargs) -> Any:
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
        self.context = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        prompt = AdvancedSecurityAgentPrompt(query=input_query, context=self.context)
        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {"content_type": "prompt", "value": prompt.to_string()},
        )
