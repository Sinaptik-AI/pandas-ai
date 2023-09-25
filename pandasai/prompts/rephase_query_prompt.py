""" Prompt to rephrase query to get more accurate responses
You are provided with the following pandas DataFrames:

{dataframes}

and based on our conversation:

<conversation>
{conversation}
</conversation>

Return the rephrased sentence of  "{query}”  in order to obtain more accurate and 
comprehensive responses without any explanations.

"""
from typing import List

import pandas as pd
from .base import Prompt


class RephraseQueryPrompt(Prompt):
    """Prompt to rephrase query to get more accurate responses"""

    text: str = """
You are provided with the following pandas DataFrames:

{dataframes}

And based on our conversation:

<conversation>
{conversation}
</conversation>

Return the rephrased sentence of "{query}” in order to obtain more accurate and 
comprehensive responses without any explanations.

"""

    def __init__(self, query: str, dataframes: List[pd.DataFrame], conversation: str):
        self.set_var("query", query)
        self.set_var("conversation", conversation)
        self.set_var("dfs", dataframes)
