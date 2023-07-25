""" Prompt to correct Python Code on Error
```
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above
mentioned error. Do not generate the same code again. Make sure to prefix the requested python
code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly.
```
"""  # noqa: E501

from pandasai.constants import END_CODE_TAG, START_CODE_TAG
from .base import Prompt


class CorrectErrorPrompt(Prompt):
    """Prompt to Correct Python code on Error"""

    text: str = """
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
Make sure to prefix the requested python code with <startCode> exactly and suffix the code with <endCode> exactly.
"""  # noqa: E501

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            START_CODE_TAG=START_CODE_TAG,
            END_CODE_TAG=END_CODE_TAG,
        )
