"""Unit tests for the correct error prompt class"""

import pandas as pd
from pandasai import SmartDataframe
from pandasai.prompts import CorrectErrorPrompt
from pandasai.llm.fake import FakeLLM


class TestCorrectErrorPrompt:
    """Unit tests for the correct error prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        llm = FakeLLM("plt.show()")
        dfs = [
            SmartDataframe(
                pd.DataFrame({}),
                config={"llm": llm},
            )
        ]

        assert (
            str(
                CorrectErrorPrompt(
                    conversation="What is the correct code?",
                    error_returned="Error message",
                    code="df.head()",
                    engine="pandas",
                    dfs=dfs,
                )
            )
            == """
You are provided with the following pandas DataFrames with the following metadata:

Dataframe dfs[0], with 0 rows and 0 columns.
This is the metadata of the dataframe dfs[0]:



The user asked the following question:
What is the correct code?

You generated this python code:
df.head()

It fails with the following error:
Error message

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
"""  # noqa: E501
        )
