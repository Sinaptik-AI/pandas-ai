"""Unit tests for the generate python code prompt class"""
import sys

import pandas as pd
import pytest
from pandasai.prompts import GeneratePythonCodePrompt
from pandasai.connectors import PandasConnector
from pandasai import Agent
from pandasai.llm.fake import FakeLLM


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    @pytest.mark.parametrize(
        "output_type,output_type_template",
        [
            *[
                (
                    "",
                    """type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }""",
                ),
                (
                    "number",
                    """type (must be "number"), value must int. Example: { "type": "number", "value": 125 }""",
                ),
                (
                    "dataframe",
                    """type (must be "dataframe"), value must be pd.DataFrame or pd.Series. Example: { "type": "dataframe", "value": pd.DataFrame({...}) }""",
                ),
                (
                    "plot",
                    """type (must be "plot"), value must be string. Example: { "type": "plot", "value": "temp_chart.png" }""",
                ),
                (
                    "string",
                    """type (must be "string"), value must be string. Example: { "type": "string", "value": f"The highest salary is {highest_salary}." }""",
                ),
            ]
        ],
    )
    def test_str_with_args(self, output_type, output_type_template):
        """Test casting of prompt to string and interpolation of context.

        Args:
            output_type (str): output type
            output_type_template (str): output type template

        Returns:
            None
        """
        llm = FakeLLM()
        agent = Agent(
            PandasConnector({"original_df": pd.DataFrame({"a": [1], "b": [4]})}),
            config={"llm": llm},
        )
        prompt = GeneratePythonCodePrompt(
            context=agent.context,
            output_type=output_type,
        )

        expected_prompt_content = f"""<dataframe>
dfs[0]:1x2
a,b
1,4
</dataframe>






Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: 
{output_type_template}

```



Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.


Generate python code and return full updated code:"""  # noqa E501
        actual_prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            actual_prompt_content = actual_prompt_content.replace("\r\n", "\n")
        assert actual_prompt_content == expected_prompt_content
