import datetime
from typing import Any

from pandasai.ee.agents.judge_agent.prompts.judge_agent_prompt import JudgeAgentPrompt
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.judge.judge_pipeline_input import JudgePipelineInput
from pandasai.pipelines.logic_unit_output import LogicUnitOutput


class JudgePromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

    def execute(self, input_data: JudgePipelineInput, **kwargs) -> Any:
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

        now = datetime.datetime.now()
        human_readable_datetime = now.strftime("%A, %B %d, %Y %I:%M %p")

        prompt = JudgeAgentPrompt(
            query=input_data.query,
            code=input_data.code,
            context=self.context,
            date=human_readable_datetime,
        )
        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {"content_type": "prompt", "value": prompt.to_string()},
        )
