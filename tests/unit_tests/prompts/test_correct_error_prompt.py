"""Unit tests for the correct error prompt class"""
import sys

import pandas as pd

from pandasai import SmartDataframe
from pandasai.llm.fake import FakeLLM
from pandasai.prompts import CorrectErrorPrompt


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
        prompt = CorrectErrorPrompt(
            engine="pandas", code="df.head()", error_returned="Error message"
        )
        prompt.set_var("dfs", dfs)
        prompt.set_var("conversation", "What is the correct code?")
        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        assert (
            prompt_content
            == """<dataframe>
dfs[0]:0x0

</dataframe>

The user asked the following question:
What is the correct code?

You generated this python code:
df.head()

It fails with the following error:
Error message

Fix the python code above and return the new python code:"""  # noqa: E501
        )
