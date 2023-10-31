from logging import Logger
from typing import Optional
from pandasai.pipelines.logic_units.output_logic_unit import ProcessOutput
from pandasai.pipelines.synthetic_dataframe.synthetic_df_prompt import (
    SyntheticDataframePrompt,
)
from pandasai.pipelines.synthetic_dataframe.sdf_code_executor import (
    SDFCodeExecutor,
)
from pandasai.pipelines.logic_units.prompt_execution import PromptExecution
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext


class GenerateSDFPipeline:
    _pipeline: Pipeline

    def __init__(
        self,
        amount: int = 100,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self._pipeline = Pipeline(
            context=context,
            logger=logger,
            steps=[
                SyntheticDataframePrompt(amount=amount),
                PromptExecution(),
                SDFCodeExecutor(),
                ProcessOutput(),
            ],
        )

    def run(self):
        return self._pipeline.run()
