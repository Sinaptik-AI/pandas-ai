""" Prompt to get clarification questions
You are provided with the following pandas DataFrames:

<dataframe>
{dataframe}
</dataframe>

<conversation>
{conversation}
</conversation>

Based on the conversation, are there any clarification questions that a senior data scientist would ask? These are questions for non technical people, only ask for questions they could ask given low tech expertise and no knowledge about how the dataframes are structured.

Return the JSON array of the clarification questions. If there is no clarification question, return an empty array.

Json:
"""  # noqa: E501


from .base import Prompt


class ClarificationQuestionPrompt(Prompt):
    """Prompt to get clarification questions"""

    text: str = """
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

Based on the conversation, are there any clarification questions 
that a senior data scientist would ask? These are questions for non technical people, 
only ask for questions they could ask given low tech expertise and 
no knowledge about how the dataframes are structured.

Return the JSON array of the clarification questions. 

If there is no clarification question, return an empty array.

Json:
"""

    def __init__(self, dataframes, conversation):
        self.set_var("dfs", dataframes)
        self.set_var("conversation", conversation)
