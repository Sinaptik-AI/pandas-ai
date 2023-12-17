from typing import Any
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext
from ...prompts.generate_python_code import GeneratePythonCodePrompt
from ...prompts.direct_sql_prompt import DirectSQLPrompt
from ...prompts.file_based_prompt import FileBasedPrompt
from ...helpers.viz_library_types.base import VisualizationLibrary
from ...helpers.viz_library_types import viz_lib_type_factory
from ...prompts.base import AbstractPrompt
from ...helpers.logger import Logger


class PromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

    def _get_chat_prompt(self, context: PipelineContext) -> [str, FileBasedPrompt]:
        key = (
            "direct_sql_prompt" if context.config.direct_sql else "generate_python_code"
        )
        return (
            key,
            (
                DirectSQLPrompt(tables=context.dfs)
                if context.config.direct_sql
                else GeneratePythonCodePrompt()
            ),
        )

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method will return output according to
        Implementation.

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        viz_lib = VisualizationLibrary.DEFAULT.value
        if self.context.config.data_viz_library:
            viz_lib = self.context.config.data_viz_library.value
        viz_lib_helper = viz_lib_type_factory(viz_lib, logger=kwargs.get("logger"))

        default_values = {
            "output_type_hint": self.context.get("output_type_helper").template_hint,
            "viz_library_type": viz_lib_helper.template_hint,
        }

        if (
            self.context.memory.size > 1
            and self.context.memory.count() > 1
            and self.context.get("last_code_generated")
        ):
            default_values["current_code"] = self.context.get("last_code_generated")
            default_values["code_description"] = ""

        return self.context.query_exec_tracker.execute_func(
            self.get_prompt,
            default_values=default_values,
        )

    def get_chat_prompt(self, context: PipelineContext) -> [str, FileBasedPrompt]:
        custom_prompt_key = (
            "direct_sql_prompt" if context.config.direct_sql else "generate_python_code"
        )
        default_prompt = (
            DirectSQLPrompt(tables=context.dfs)
            if context.config.direct_sql
            else GeneratePythonCodePrompt()
        )
        return custom_prompt_key, default_prompt

    def get_prompt(self, default_values) -> AbstractPrompt:
        """
        Return a prompt by key.

        Args:
            values (dict): The values to use for the prompt

        Returns:
            AbstractPrompt: The prompt
        """
        custom_prompt_key, default_prompt = self.get_chat_prompt(self.context)
        prompt = (
            self.context.config.custom_prompts.get(custom_prompt_key) or default_prompt
        )

        # Set default values for the prompt
        prompt.set_config(self.context.config)

        # Set the variables for the prompt
        values = {
            "dfs": self.context.dfs,
            "conversation": self.context.memory.get_conversation(),
            "prev_conversation": self.context.memory.get_previous_conversation(),
            "last_message": self.context.memory.get_last_message(),
            "skills": self.context.skills_manager.prompt_display() or "",
        }
        values |= default_values
        prompt.set_vars(values)

        self.logger.log(f"Using prompt: {prompt}")
        return prompt
