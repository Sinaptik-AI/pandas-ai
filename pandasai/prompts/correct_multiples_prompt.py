""" Prompt to correct error """

import pandas as pd

from pandasai.constants import END_CODE_TAG, START_CODE_TAG

from .base import Prompt


class CorrectMultipleDataframesErrorPrompt(Prompt):
    """Prompt to generate Python code"""
    # pylint: disable=too-few-public-methods

    text: str = """
You are provided with the following pandas dataframes:"""

    def __init__(
        self,
        code: str,
        error_returned: Exception,
        question: str,
        df_head: list[pd.DataFrame],
    ): # pylint: disable=super-init-not-called
        for i, dataframe in enumerate(df_head, start=1):
            row, col = dataframe.shape
            self.text += f"""
Dataframe df{i}, with {row} rows and {col} columns.
This is the result of `print(df{i}.head())`:
{dataframe}"""

        instruction: str = f"""
The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
Make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly.
"""

        self.text += instruction

    def __str__(self):
        return self.text
