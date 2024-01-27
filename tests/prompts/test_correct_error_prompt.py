"""Unit tests for the correct error prompt class"""
import sys

import pandas as pd
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.prompts import CorrectErrorPrompt
from pandasai.connectors import PandasConnector
from pandasai import Agent
from pandasai.llm.fake import FakeLLM


class TestCorrectErrorPrompt:
    """Unit tests for the correct error prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        llm = FakeLLM()
        agent = Agent(
            dfs=[PandasConnector({"original_df": pd.DataFrame()})],
            config={"llm": llm, "dataframe_serializer": DataframeSerializerType.CSV},
        )
        prompt = CorrectErrorPrompt(
            context=agent.context, code="df.head()", error="Error message"
        )
        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        assert (
            prompt_content
            == """<dataframe>
dfs[0]:0x0

</dataframe>

The user asked the following question:


You generated this python code:
df.head()

It fails with the following error:
Error message

Fix the python code above and return the new python code:"""  # noqa: E501
        )
