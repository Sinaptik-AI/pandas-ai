""" Prompt to generate the response to the question in a conversational way
```
Question: {question}
Answer: {answer}

Rewrite the answer to the question in a conversational way.
```

"""

from .base import Prompt


class GenerateResponsePrompt(Prompt):
    """Prompt to generate the response to the question in a conversational way"""
    # pylint: disable=too-few-public-methods

    text: str = """
Question: {question}
Answer: {answer}

Rewrite the answer to the question in a conversational way.
"""
