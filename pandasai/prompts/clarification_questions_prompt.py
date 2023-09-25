""" Prompt to get clarification questions
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

Based on the conversation, are there any clarification questions that a senior data scientist would ask? These are questions for non technical people, only ask for questions they could ask given low tech expertise and no knowledge about how the dataframes are structured.

Return the JSON array of the clarification questions. If there is no clarification question, return an empty array.

Json:
"""  # noqa: E501


from typing import List
import pandas as pd
from .base import Prompt


class ClarificationQuestionPrompt(Prompt):
    """Prompt to get clarification questions"""

    text: str = """
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

Based on the conversation, are there any clarification questions that a senior data scientist would ask about the query "{query}"?

It is extremely important that you follow the following guidelines when generating clarification questions:
- Ask questions a non technical person could answer. Do not include technical terms, do not ask for questions that require knowledge about how the dataframes are structured or about a specific column.
- Only ask for questions related to the query if the query is not clear or ambiguous and that cannot be deduced from the context.
- Return a maximum of 3 questions. The lower the number of questions, the better.
- If no meaningful clarification questions can be asked, return an empty array.

Return the JSON array of the clarification questions. 

Json:
"""  # noqa: E501

    def __init__(self, dataframes: List[pd.DataFrame], conversation: str, query: str):
        self.set_var("dfs", dataframes)
        self.set_var("conversation", conversation)
        self.set_var("query", query)
