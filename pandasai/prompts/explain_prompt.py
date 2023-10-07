""" Prompt to explain code generation by the LLM
The previous conversation we had

<Conversation>
{conversation}
</Conversation>

Based on the last conversation you generated the following code:

<Code>
{code}
</Code>

Explain how you came up with code for non-technical people without 
mentioning technical details or mentioning the libraries used?

"""
from .file_based_prompt import FileBasedPrompt


class ExplainPrompt(FileBasedPrompt):
    """Prompt to explain code generation by the LLM"""

    _path_to_template = "assets/prompt_templates/explain_prompt.tmpl"

    def setup(self, conversation: str, code: str) -> None:
        self.set_var("conversation", conversation)
        self.set_var("code", code)
