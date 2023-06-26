""" Prompt to correct error """

import pandas as pd

from .base import Prompt


class CorrectMultipleDataframesErrorPrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
You are provided with the following pandas dataframes:"""

    def __init__(
        self,
        code: str,
        error_returned: Exception,
        question: str,
        df_head: list[pd.DataFrame],
    ):
        for i, dataframe in enumerate(df_head, start=1):
            row, col = dataframe.shape
            self.text += f"""
Dataframe df{i}, with {row} rows and {col} columns.
This is the metadata of the dataframe df{i}:
{dataframe}"""

        instruction: str = f"""
The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
"""  # noqa: E501

        self.text += instruction

    def __str__(self):
        return self.text
