""" Prompt to generate Python code
```
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the
dataframe `df`. Using the provided dataframe, df, return the python code to get the answer to the following question:
```
"""  # noqa: E501

from datetime import date

from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the dataframe `df`.
Using the provided dataframe, df, return the python code to get the answer to the following question:
"""  # noqa: E501

    def __init__(self, **kwargs):
        super().__init__(**kwargs, today_date=date.today())
