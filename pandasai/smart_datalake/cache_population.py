from typing import Any
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext


class CachePopulation(BaseLogicUnit):
    """
    Cache Population Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        pipeline_context: PipelineContext = kwargs.get("context")

        if self.skip_if is not None and self.skip_if(pipeline_context):
            return input

        code = input

        if pipeline_context.config.enable_cache and pipeline_context.cache:
            pipeline_context.cache.set(
                pipeline_context.cache.get_cache_key(pipeline_context), code
            )

        if pipeline_context.config.callback is not None:
            pipeline_context.config.callback.on_code(code)

        return code
