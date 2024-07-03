from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class BaseSecurity:
    context: PipelineContext
    pipeline: Pipeline
    logger: Logger

    def __init__(
        self,
        pipeline: Pipeline,
    ) -> None:
        self.pipeline = pipeline

    def evaluate(self, query: str) -> bool:
        raise NotImplementedError
