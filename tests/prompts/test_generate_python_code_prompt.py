"""Unit tests for the generate python code prompt class"""
import sys

import pandas as pd
from pandasai import SmartDataframe
from pandasai.prompts import GeneratePythonCodeAbstractPrompt
from pandasai.llm.fake import FakeLLM


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        llm = FakeLLM("plt.show()")
        dfs = [
            SmartDataframe(
                pd.DataFrame({"a": [1], "b": [4]}),
                config={"llm": llm},
            )
        ]
        prompt = GeneratePythonCodeAbstractPrompt()
        prompt.set_var("dfs", dfs)
        prompt.set_var("conversation", "Question")
        prompt.set_var("save_charts_path", "exports/charts")

        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        assert (
            prompt_content
            == """
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
    \"\"\"
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in exports/charts/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    - type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Example output: { "type": "text", "value": "The average loan amount is $15,000." }
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.

Updated code:
"""  # noqa: E501
        )

    def test_str_with_custom_save_charts_path(self):
        """Test that the __str__ method is implemented"""

        llm = FakeLLM("plt.show()")
        dfs = [
            SmartDataframe(
                pd.DataFrame({"a": [1], "b": [4]}),
                config={"llm": llm},
            )
        ]

        prompt = GeneratePythonCodeAbstractPrompt()
        prompt.set_var("dfs", dfs)
        prompt.set_var("conversation", "Question")
        prompt.set_var("save_charts_path", "custom_path")

        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        assert (
            prompt_content
            == """
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
    \"\"\"
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in custom_path/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    - type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Example output: { "type": "text", "value": "The average loan amount is $15,000." }
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.

Updated code:
"""  # noqa: E501
        )
