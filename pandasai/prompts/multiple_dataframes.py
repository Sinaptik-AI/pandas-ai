""" Prompt to generate Python code for multiple dataframes """

from datetime import date

import pandas as pd

from pandasai.constants import END_CODE_TAG, START_CODE_TAG

from .base import Prompt


class MultipleDataframesPrompt(Prompt):
    """Prompt to generate Python code"""
    # pylint: disable=too-few-public-methods

    text: str = """
Today is {today_date}.
You are provided with the following pandas dataframes:"""
    instruction: str = """
When asked about the data, your response should include a python code that describes the dataframes provided.
Using the provided dataframes and no other dataframes, return the python code and make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly to get the answer to the following question:
"""

    def __init__(self, dataframes: list[pd.DataFrame]): # pylint: disable=super-init-not-called
        for i, dataframe in enumerate(dataframes, start=1):
            row, col = dataframe.shape

            self.text += f"""
Dataframe df{i}, with {row} rows and {col} columns.
This is the result of `print(df{i}.head())`:
{dataframe}"""

        self.text += self.instruction
        self.text = self.text.format(
            today_date=date.today(),
            START_CODE_TAG=START_CODE_TAG,
            END_CODE_TAG=END_CODE_TAG,
        )

    def __str__(self):
        return self.text
