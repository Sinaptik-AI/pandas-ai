""" Prompt to check if the query is related to the previous conversation

<conversation>
{conversation}
</conversation>

<query>
{query}
</query>

Is the query related to the conversation? Answer only "true" or "false" (lowercase).
"""
from .file_based_prompt import FileBasedPrompt


class CheckIfRelevantToConversationPrompt(FileBasedPrompt):
    """Prompt to check if the query is related to the previous conversation"""

    _path_to_template = "assets/prompt_templates/check_if_relevant_to_conversation.tmpl"
