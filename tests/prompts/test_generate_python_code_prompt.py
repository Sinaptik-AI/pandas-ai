"""Unit tests for the generate python code prompt class"""


import pandas as pd
from pandasai import SmartDataframe
from pandasai.prompts import GeneratePythonCodePrompt
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
        assert (
            str(
                GeneratePythonCodePrompt(
                    engine="pandas", conversation="Question", dfs=dfs
                )
            )
            == """
You are provided with the following pandas DataFrames with the following metadata:

Dataframe dfs[0], with 1 rows and 2 columns.
This is the metadata of the dataframe dfs[0]:
a,b
1,4


This is the initial python code to be updated:
```python
# TODO import all the dependencies required
import pandas as pd

# Analyze the data
# 1. Prepare: Preprocessing and cleaning data if necessary
# 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
# 3. Analyze: Conducting the actual analysis (if the user asks to create a chart save it to an image in exports/charts/temp_chart.png and do not show the chart.)
# 4. Output: return a dictionary of:
# - type (possible values "text", "number", "dataframe", "plot")
# - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
# Example output: { "type": "text", "value": "The average loan amount is $15,000." }
def analyze_data(dfs: list[pd.DataFrame]) -> dict:
   # Code goes here (do not add comments)
    

# Declare a result variable
result = analyze_data(dfs)
```

Using the provided dataframes (`dfs`), update the python code based on the last user question:
Question

Updated code:
"""  # noqa: E501
        )
