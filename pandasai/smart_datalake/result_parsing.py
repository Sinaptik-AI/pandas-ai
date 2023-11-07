from typing import Any
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext


class ResultParsing(BaseLogicUnit):

    """
    Result Parsing Stage
    """

    def execute(self, input: Any, **kwargs) -> Any:
        pipeline_context: PipelineContext = kwargs.get("context")

        result = input

        self._add_result_to_memory(result=result, context=pipeline_context)

        result = pipeline_context.query_exec_tracker.execute_func(
            pipeline_context.get_intermediate_value("response_parser").parse, result
        )
        return result

    def _add_result_to_memory(self, result: dict, context: PipelineContext):
        """
        Add the result to the memory.

        Args:
            result (dict): The result to add to the memory
            context (PipelineContext) : Pipleline Context
        """
        if result is None:
            return

        if result["type"] in ["string", "number"]:
            context.memory.add(result["value"], False)
        elif result["type"] in ["dataframe", "plot"]:
            context.memory.add("Ok here it is", False)
