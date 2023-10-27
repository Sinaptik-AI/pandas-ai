from typing import Any
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.prompts.generate_synthetic_df_prompt import GenerateSyntheticDfPrompt


class SyntheticDataframePrompt(BaseLogicUnit):
    """
    Generates the prompt for generating synthetic dataframe
    """

    def execute(self, input: Any, **kwargs) -> Any:
        context: PipelineContext = kwargs["context"]

        if context is None or len(context.dfs) == 0:
            raise ValueError("Dataframe not found")

        prompt = GenerateSyntheticDfPrompt()

        prompt.set_var("dataframe", context.dfs[0])

        return prompt
