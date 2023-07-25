""" Prompt to generate Python code
```
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the
dataframe `df`. Using the provided dataframe, df, return the python code and make sure to prefix
the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG}
exactly to get the answer to the following question:
```
"""  # noqa: E501


from pandasai.constants import END_CODE_TAG, START_CODE_TAG
from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the dataframe `df`.
Using the provided dataframe, df, return the python code and make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly to get the answer to the following question:
"""  # noqa: E501

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs, START_CODE_TAG=START_CODE_TAG, END_CODE_TAG=END_CODE_TAG
        )
