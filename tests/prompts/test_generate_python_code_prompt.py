"""Unit tests for the generate python code prompt class"""

from datetime import date

import pytest

from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""
        assert (
            str(
                GeneratePythonCodePrompt(
                    df_head="df.head()",
                    num_rows=10,
                    num_columns=5,
                    rows_to_display=5,
                )
            )
            == f"""
Today is {date.today()}.
You are provided with a pandas dataframe (df) with 10 rows and 5 columns.
This is the result of `print(df.head(5))`:
df.head().

When asked about the data, your response should include a python code that describes the dataframe `df`.
Using the provided dataframe, df, return the python code and make sure to prefix the requested python code with <startCode> exactly and suffix the code with <endCode> exactly to get the answer to the following question:
"""
        )
