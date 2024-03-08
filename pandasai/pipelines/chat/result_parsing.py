from typing import Any

from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ...responses.context import Context
from ...responses.response_parser import ResponseParser
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class ResultParsing(BaseLogicUnit):

    """
    Result Parsing Stage
    """

    pass

    def response_parser(self, context: PipelineContext, logger) -> ResponseParser:
        context = Context(context.config, logger=logger)
        return (
            context.config.response_parser(context)
            if context.config.response_parser
            else ResponseParser(context)
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

        result = input

        self._add_result_to_memory(result=result, context=pipeline_context)

        parser = self.response_parser(pipeline_context, logger=kwargs.get("logger"))
        result = parser.parse(result)
        return LogicUnitOutput(result, True, "Results parsed successfully")

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
            context.memory.add(str(result["value"]), False)
        elif result["type"] == "dataframe":
            context.memory.add("Check it out: <dataframe>", False)
        elif result["type"] == "plot":
            context.memory.add("Check it out: <plot>", False)
