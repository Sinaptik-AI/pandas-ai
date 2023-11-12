from typing import Any
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext
from ...prompts.generate_python_code import GeneratePythonCodePrompt


class PromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

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

        return pipeline_context.query_exec_tracker.execute_func(
            pipeline_context.get_intermediate_value("get_prompt"),
            "generate_python_code",
            default_prompt=GeneratePythonCodePrompt(),
            default_values=default_values,
        )
