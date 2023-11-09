from typing import Any
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext


class CacheLookup(BaseLogicUnit):
    """
    Cache Lookup of Code Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
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
            code = pipeline_context.query_exec_tracker.execute_func(
                pipeline_context.cache.get,
                pipeline_context.cache.get_cache_key(pipeline_context),
                tag="cache_hit",
            )
            pipeline_context.add_intermediate_value("is_present_in_cache", True)
            return code
