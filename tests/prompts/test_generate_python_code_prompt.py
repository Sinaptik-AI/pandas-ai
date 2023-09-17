"""Unit tests for the generate python code prompt class"""
import sys

import pandas as pd
import pytest

from pandasai import SmartDataframe
from pandasai.helpers.output_types import (
    output_type_factory,
    DefaultOutputType,
    output_types_map,
)
from pandasai.prompts import GeneratePythonCodePrompt
from pandasai.llm.fake import FakeLLM


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    @pytest.mark.parametrize(
        "save_charts_path,output_type_hint",
        [
            ("exports/charts", DefaultOutputType().template_hint),
            ("custom/dir/for/charts", DefaultOutputType().template_hint),
            *[
                ("exports/charts", output_type_factory(type_).template_hint)
                for type_ in output_types_map
            ],
        ],
    )
    def test_str_with_args(self, save_charts_path, output_type_hint):
        """Test casting of prompt to string and interpolation of context.

        Parameterized for the following cases:
        * `save_charts_path` is "exports/charts", `output_type_hint` is default
        * `save_charts_path` is "custom/dir/for/charts", `output_type_hint`
            is default
        * `save_charts_path` is "exports/charts", `output_type_hint` any of
            possible types in `pandasai.helpers.output_types.output_types_map`
        """

        llm = FakeLLM("plt.show()")
        dfs = [
            SmartDataframe(
                pd.DataFrame({"a": [1], "b": [4]}),
                config={"llm": llm},
            )
        ]
        prompt = GeneratePythonCodePrompt(output_type_hint=output_type_hint)
        prompt.set_var("dfs", dfs)
        prompt.set_var("conversation", "Question")
        prompt.set_var("save_charts_path", save_charts_path)

        expected_prompt_content = f'''
You are provided with the following pandas DataFrames:

<dataframe>
Dataframe dfs[0], with 1 rows and 2 columns.
This is the metadata of the dataframe dfs[0]:
a,b
1,4
</dataframe>

<conversation>
Question
</conversation>

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
import pandas as pd

def analyze_data(dfs: list[pd.DataFrame]) -> dict:
    """
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in {save_charts_path}/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    {output_type_hint}
    Example output: {{ "type": "text", "value": "The average loan amount is $15,000." }}
    """
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.

Updated code:
'''  # noqa E501
        actual_prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            actual_prompt_content = actual_prompt_content.replace("\r\n", "\n")
        assert actual_prompt_content == expected_prompt_content
