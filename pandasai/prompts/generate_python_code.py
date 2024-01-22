from .base import BasePrompt


class GeneratePythonCodePrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "generate_python_code.tmpl"
