""" Prompt to explain solution generated
Based on the last conversation you generated the code. 
Can you explain briefly for non technical person on how you came up with code 
without explaining pandas library?
"""


from .base import Prompt


class ExplainPrompt(Prompt):
    """Prompt to get clarification questions"""

    text: str = """
The previous conversation we had

<Conversation>
{conversation}
</Conversation>

Based on the last conversation you generated the code. 

<Code>
{code}
</Code

Can you explain briefly for non technical person on how you came up with code 
without explaining pandas library?

"""
