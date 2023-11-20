from typing import Any
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.prompts.generate_synthetic_df_prompt import GenerateSyntheticDfPrompt


class SyntheticDataframePrompt(BaseLogicUnit):
    """
    Generates the prompt for generating synthetic dataframe
    """

    _amount: int = 100

    def __init__(self, amount: int = 100):
        """
        Initialize the logic unit with the given parameters
        Args:
            amount (int): Amount of rows to generate
        """
        self._amount = amount

    def execute(self, input: Any, **kwargs) -> Any:
        context: PipelineContext = kwargs.get("context")
        logger = kwargs.get("logger")

        if context is None or len(context.dfs) == 0:
            raise ValueError("Dataframe not found")

        prompt = GenerateSyntheticDfPrompt(
            amount=self._amount,
            dataframe=context.dfs[kwargs.get("dataframe_index", 0)],
        )
        logger.log(f"Generate Prompt: {prompt}")

        return prompt
