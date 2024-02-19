from typing import Any

from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class CachePopulation(BaseLogicUnit):
    """
    Cache Population Stage
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

        code = input

        if pipeline_context.config.enable_cache and pipeline_context.cache:
            pipeline_context.cache.set(
                pipeline_context.cache.get_cache_key(pipeline_context), code
            )

        return LogicUnitOutput(
            code,
            True,
            "Prompt Cached Successfully"
            if pipeline_context.config.enable_cache
            else "Caching disabled",
        )
