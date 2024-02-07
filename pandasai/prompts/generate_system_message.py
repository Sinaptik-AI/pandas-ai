from .base import BasePrompt


class GenerateSystemMessagePrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "generate_system_message.tmpl"
