from typing import Any
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext
from ...prompts.generate_python_code import GeneratePythonCodePrompt
from ...prompts.direct_sql_prompt import DirectSQLPrompt
from ...prompts.file_based_prompt import FileBasedPrompt


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
        pipeline_context: PipelineContext = kwargs.get("context")

        default_values = {
            # TODO: find a better way to determine the engine,
            "engine": pipeline_context.dfs[0].engine,
            "output_type_hint": pipeline_context.get_intermediate_value(
                "output_type_helper"
            ).template_hint,
            "viz_library_type": pipeline_context.get_intermediate_value(
                "viz_lib_helper"
            ).template_hint,
        }

        if (
            pipeline_context.memory.size > 1
            and pipeline_context.memory.count() > 1
            and pipeline_context.get_intermediate_value("last_code_generated")
        ):
            default_values["current_code"] = pipeline_context.get_intermediate_value(
                "last_code_generated"
            )
            default_values["code_description"] = ""

        [key, default_prompt] = self._get_chat_prompt(pipeline_context)

        return pipeline_context.query_exec_tracker.execute_func(
            pipeline_context.get_intermediate_value("get_prompt"),
            key=key,
            default_prompt=default_prompt,
            default_values=default_values,
        )
