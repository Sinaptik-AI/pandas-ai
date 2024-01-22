from .base import BasePrompt


class CorrectErrorPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "correct_error_prompt.tmpl"
