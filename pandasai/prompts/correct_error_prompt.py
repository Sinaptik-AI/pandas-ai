""" Prompt to correct Python Code on Error
```
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the result of `print(df.head({rows_to_display}))`:
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
"""
# pylint:disable=duplicate-code
from datetime import date

from pandasai.constants import END_CODE_TAG, START_CODE_TAG

from .base import Prompt


class CorrectErrorPrompt(Prompt):
    """Prompt to Correct Python code on Error"""
    # pylint: disable=too-few-public-methods

    text: str = """
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the result of `print(df.head({rows_to_display}))`:
{df_head}.

The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
Make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly.
"""

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            START_CODE_TAG=START_CODE_TAG,
            END_CODE_TAG=END_CODE_TAG,
            today_date=date.today()
        )
