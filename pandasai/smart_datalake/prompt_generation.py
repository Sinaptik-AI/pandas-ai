from typing import Any
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class PromptGeneration(BaseLogicUnit):
    """
    Code Prompt Generation Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        pipeline_context: PipelineContext = kwargs.get("context")

        if self.skip_if is not None and self.skip_if(pipeline_context):
            return input

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

        generate_python_code_instruction = (
            pipeline_context.query_exec_tracker.execute_func(
                pipeline_context.get_intermediate_value("get_prompt"),
                "generate_python_code",
                default_prompt=GeneratePythonCodePrompt,
                default_values=default_values,
            )
        )

        return generate_python_code_instruction
