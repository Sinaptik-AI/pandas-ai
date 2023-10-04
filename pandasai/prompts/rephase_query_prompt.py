""" Prompt to rephrase query to get more accurate responses
You are provided with the following pandas DataFrames:

{dataframes}
{conversation}

Use the provided dataframe and conversation we have had to Return the rephrased 
sentence of "{query}” in order to obtain more accurate and comprehensive responses 
without any explanations.
"""
from typing import List

import pandas as pd
from .base import FileBasedPrompt


class RephraseQueryPrompt(FileBasedPrompt):
    """Prompt to rephrase query to get more accurate responses"""

    _path_to_template = "assets/prompt_templates/rephrase_query_prompt.tmpl"

    def __init__(
        self, query: str, dataframes: List[pd.DataFrame], conversation: str, **kwargs
    ):
        conversation_content = (
            self.conversation_text.format(conversation=conversation)
            if conversation
            else ""
        )
        self.set_var("conversation", conversation_content)
        self.set_var("query", query)
        self.set_var("dfs", dataframes)

        super().__init__(**kwargs)
