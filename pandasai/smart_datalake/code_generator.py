from typing import Any
from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.base_logic_unit import BaseLogicUnit


class CodeGenerator(BaseLogicUnit):
    """
    LLM Code Generation Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        pipeline_context: PipelineContext = kwargs.get("context")
        logger: Logger = kwargs.get("logger")

        if self.skip_if is not None and self.skip_if(pipeline_context):
            return input

        generate_python_code_instruction = input

        [
            code,
            reasoning,
            answer,
        ] = pipeline_context.query_exec_tracker.execute_func(
            pipeline_context.config.llm.generate_code,
            generate_python_code_instruction,
        )
        pipeline_context.add_intermediate_value("last_code_generated", code)
        logger.log(
            f"""Code generated:
            ```
            {code}
            ```
            """
        )
        pipeline_context.add_intermediate_value("last_reasoning", reasoning)
        pipeline_context.add_intermediate_value("last_answer", answer)

        return code
