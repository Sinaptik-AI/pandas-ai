"""Google Palm LLM"""
from .base import BaseGoogle


class GooglePalm(BaseGoogle):
    """Google Palm LLM"""

    model: str = "models/text-bison-001"

    def __init__(self, api_key: str, **kwargs):
        self._configure(api_key=api_key)
        self._set_params(**kwargs)

    def _valid_params(self):
        return super()._valid_params() + ["model"]

    def _validate(self):
        super()._validate()

        if not self.model:
            raise ValueError("model is required.")

    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        self._validate()
        completion = self.genai.generate_text(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        return completion.result

    @property
    def type(self) -> str:
        return "google-palm"
