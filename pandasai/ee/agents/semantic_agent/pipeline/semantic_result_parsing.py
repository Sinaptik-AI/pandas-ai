from pandasai.pipelines.chat.result_parsing import ResultParsing
from pandasai.pipelines.pipeline_context import PipelineContext


class SemanticResultParser(ResultParsing):
    """
    Semantic Agent Result Parsing Stage
    """

    pass

    def _add_result_to_memory(self, result: dict, context: PipelineContext):
        """
        Add the result to the memory.

        Args:
            result (dict): The result to add to the memory
            context (PipelineContext) : Pipeline Context
        """
        if result is None:
            return

        context.memory.add(context.get("llm_call"), False)
