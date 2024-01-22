from .base import BasePrompt


class CorrectOutputTypeErrorPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "correct_output_type_error_prompt.tmpl"
