from typing import Any
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class ResultParsing(BaseLogicUnit):

    """
    Result Parsing Stage
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
            context (PipelineContext) : Pipeline Context
        """
        if result is None:
            return

        if result["type"] in ["string", "number"]:
            context.memory.add(result["value"], False)
        elif result["type"] == "dataframe":
            context.memory.add("Check it out: <dataframe>", False)
        elif result["type"] == "plot":
            context.memory.add("Check it out: <plot>", False)
