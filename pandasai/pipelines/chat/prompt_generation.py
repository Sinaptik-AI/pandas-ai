from typing import Any, Union

# from pandasai.helpers.openai import is_openai_format_llm
from pandasai.helpers.optional import is_openai_format_llm
from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ...helpers.logger import Logger
from ...prompts.base import BasePrompt
from ...prompts.generate_python_code import GeneratePythonCodePrompt
from ...prompts.generate_python_code_with_sql import GeneratePythonCodeWithSQLPrompt
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


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
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        prompt = self.get_chat_prompt(self.context)
        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {"content_type": "prompt", "value": prompt.to_string()},
        )

    def get_chat_prompt(self, context: PipelineContext) -> Union[str, BasePrompt]:
        # set matplotlib as the default library
        viz_lib = "matplotlib"
        if context.config.data_viz_library:
            viz_lib = context.config.data_viz_library

        use_train_qa = not is_openai_format_llm(context.config.llm)
        output_type = context.get("output_type")

        if not use_train_qa:
            # Add context of qa to agent memory
            context.memory.add_qa_to_memory_for_query(
                context.vectorstore.get_relevant_qa_documents(
                    context.memory.get_last_message()
                )
            )

        return (
            GeneratePythonCodeWithSQLPrompt(
                context=context,
                last_code_generated=context.get("last_code_generated"),
                viz_lib=viz_lib,
                output_type=output_type,
                use_train_qa=use_train_qa,
            )
            if context.config.direct_sql
            else GeneratePythonCodePrompt(
                context=context,
                last_code_generated=context.get("last_code_generated"),
                viz_lib=viz_lib,
                output_type=output_type,
                use_train_qa=use_train_qa,
            )
        )
