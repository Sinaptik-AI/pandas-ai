from .base import BasePrompt


class RephraseQueryPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "rephrase_query.tmpl"
