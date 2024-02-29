from .base import BasePrompt


class ExplainPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "explain.tmpl"
