"""Unit tests for the correct multiples prompt class"""

from datetime import date

import pandas as pd
import pytest

from pandasai.prompts.correct_multiples_prompt import (
    CorrectMultipleDataframesErrorPrompt,
)


class TestCorrectMultipleDataframesErrorPrompt:
    """Unit tests for the correct multiples prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        df1 = pd.DataFrame(
            {"A": [10, 20, 30, 40, 50], "B": [1, 2, 3, 4, 5], "C": [2, 3, 4, 5, 6]}
        )
        df2 = pd.DataFrame(
            {"A": [10, 20, 30, 40, 50], "B": [1, 2, 3, 4, 5], "C": [2, 3, 4, 5, 6]}
        )

        assert (
            str(
                CorrectMultipleDataframesErrorPrompt(
                    code="code",
                    error_returned=Exception("error"),
                    question="question",
                    df_head=[df1, df2],
                )
            )
            == """
You are provided with the following pandas dataframes:
Dataframe df1, with 5 rows and 3 columns.
This is the result of `print(df1.head())`:
    A  B  C
0  10  1  2
1  20  2  3
2  30  3  4
3  40  4  5
4  50  5  6
Dataframe df2, with 5 rows and 3 columns.
This is the result of `print(df2.head())`:
    A  B  C
0  10  1  2
1  20  2  3
2  30  3  4
3  40  4  5
4  50  5  6
The user asked the following question:
question

You generated this python code:
code

It fails with the following error:
error

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
Make sure to prefix the requested python code with <startCode> exactly and suffix the code with <endCode> exactly.
"""
        )
