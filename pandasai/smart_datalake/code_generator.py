from typing import Any
from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class CodeGenerator(BaseLogicUnit):
    """
    LLM Code Generation Stage
    """

    def execute(self, input: Any, **kwargs) -> Any:
        pipeline_context: PipelineContext = kwargs.get("context")
        logger: Logger = kwargs.get("logger")

        if (
            pipeline_context.config.enable_cache
            and pipeline_context.cache
            and pipeline_context.cache.get(
                self._get_cache_key(context=pipeline_context)
            )
        ):
            logger.log("Using cached response")
            code = pipeline_context.query_exec_tracker.execute_func(
                pipeline_context.cache.get,
                self._get_cache_key(context=pipeline_context),
                tag="cache_hit",
            )

        else:
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
                default_values[
                    "current_code"
                ] = pipeline_context.get_intermediate_value("last_code_generated")

            generate_python_code_instruction = (
                pipeline_context.query_exec_tracker.execute_func(
                    pipeline_context.get_intermediate_value("get_prompt"),
                    "generate_python_code",
                    default_prompt=GeneratePythonCodePrompt,
                    default_values=default_values,
                )
            )

            [
                code,
                reasoning,
                answer,
            ] = pipeline_context.query_exec_tracker.execute_func(
                pipeline_context.get_intermediate_value("llm").generate_code,
                generate_python_code_instruction,
            )

            pipeline_context.add_intermediate_value("last_reasoning", reasoning)
            pipeline_context.add_intermediate_value("last_answer", answer)

            if pipeline_context.config.enable_cache and pipeline_context.cache:
                pipeline_context.cache.set(
                    self._get_cache_key(context=pipeline_context), code
                )

        if pipeline_context.config.callback is not None:
            pipeline_context.config.callback.on_code(code)

        pipeline_context.add_intermediate_value("last_code_generated", code)
        logger.log(
            f"""Code generated:
```
{code}
```
"""
        )

        return code

    def _get_cache_key(self, context: PipelineContext) -> str:
        """
        Return the cache key for the current conversation.

        Returns:
            str: The cache key for the current conversation
        """
        cache_key = context.memory.get_conversation()

        # make the cache key unique for each combination of dfs
        for df in context.dfs:
            hash = df.column_hash()
            cache_key += str(hash)

        return cache_key
