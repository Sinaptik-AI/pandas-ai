from typing import Any

from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ...helpers.logger import Logger
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class CacheLookup(BaseLogicUnit):
    """
    Cache Lookup of Code Stage
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
        logger: Logger = kwargs.get("logger")
        if (
            pipeline_context.config.enable_cache
            and pipeline_context.cache
            and pipeline_context.cache.get(
                pipeline_context.cache.get_cache_key(pipeline_context)
            )
        ):
            logger.log("Using cached response")

            code = pipeline_context.cache.get(
                pipeline_context.cache.get_cache_key(pipeline_context)
            )

            pipeline_context.add("found_in_cache", True)

            return LogicUnitOutput(code, True, "Cache Hit")
