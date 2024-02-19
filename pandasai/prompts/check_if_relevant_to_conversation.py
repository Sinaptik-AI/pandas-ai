from .base import BasePrompt


class CheckIfRelevantToConversationPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "check_if_relevant_to_conversation.tmpl"
