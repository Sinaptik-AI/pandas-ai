""" Prompt to explain code generation by the LLM
The previous conversation we had

<Conversation>
{conversation}
</Conversation>

Based on the last conversation you generated the following code:

<Code>
{code}
</Code

Explain how you came up with code for non-technical people without 
mentioning technical details or mentioning the libraries used?

"""
from .base import Prompt


class ExplainPrompt(Prompt):
    """Prompt to explain code generation by the LLM"""

    text: str = """
The previous conversation we had

<Conversation>
{conversation}
</Conversation>

Based on the last conversation you generated the following code:

<Code>
{code}
</Code

Explain how you came up with code for non-technical people without 
mentioning technical details or mentioning the libraries used?

"""

    def __init__(self, conversation: str, code: str):
        self.set_var("conversation", conversation)
        self.set_var("code", code)
