from typing import Optional
from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.smart_datalake.code_execution import CodeExecution
from pandasai.smart_datalake.code_generator import CodeGenerator
from pandasai.smart_datalake.result_parsing import ResultParsing
from pandasai.smart_datalake.result_validation import ResultValidation


class GenerateSmartDatalakePipeline:
    _pipeline: Pipeline

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self._pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                CodeGenerator(),
                CodeExecution(),
                ResultValidation(),
                ResultParsing(),
            ],
        )

    def run(self):
        return self._pipeline.run()
