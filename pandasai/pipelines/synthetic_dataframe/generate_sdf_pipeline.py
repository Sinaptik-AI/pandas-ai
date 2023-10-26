from logging import Logger
from typing import Optional, Union
from pandasai.pipelines.synthetic_dataframe.synthetic_df_prompt import (
    SyntheticDataframePrompt,
)
from pandasai.pipelines.synthetic_dataframe.sdf_code_executor import (
    SDFCodeExecutor,
)
from pandasai.pipelines.logic_units.prompt_execution import PromptExecution
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext

from pandasai.schemas.df_config import Config


class GenerateSDFPipeline:
    _pipeline: Pipeline

    def __init__(
        self,
        config: Union[Config, dict] = None,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
    ):
        self._pipeline = Pipeline(
            config=config,
            context=context,
            logger=logger,
            steps=[SyntheticDataframePrompt(), PromptExecution(), SDFCodeExecutor()],
        )

    def run(self):
        return self._pipeline.run()
