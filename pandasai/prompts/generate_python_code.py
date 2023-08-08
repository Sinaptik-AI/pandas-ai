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
You are provided with the following {engine} DataFrames with the following metadata:

{dataframes}

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
import pandas as pd

# Analyze the data
# 1. Prepare: Preprocessing and cleaning data if necessary
# 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
# 3. Analyze: Conducting the actual analysis (if generating a plot, create a figure and axes using plt.subplots() and save it to an image in exports/charts/temp_chart.png and do not show the chart.)
# 4. Output: return a dictionary of:
# - type (possible values "text", "number", "dataframe", "plot")
# - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
def analyze_data(self, dfs: list) -> dict
   # Code goes here
    

# Declare a result variable
result = analyze_data(dfs)
```

Using the provided dataframes (`dfs`), update the python code based on the last user question:
{conversation}

Updated code:
"""  # noqa: E501

    def __init__(self, **kwargs):
        dataframes = []
        for index, df in enumerate(kwargs["dfs"], start=1):
            description = "Dataframe "
            if df.table_name is not None:
                description += f"{df.table_name} (dfs[{index-1}])"
            else:
                description += f"dfs[{index-1}]"
            description += (
                f", with {df.rows_count} rows and {df.columns_count} columns."
            )
            if df.table_description is not None:
                description += f"\nDescription: {df.table_description}"
            description += f"""
This is the metadata of the dataframe dfs[{index-1}]:
{df.head_csv}"""  # noqa: E501
            dataframes.append(description)

        super().__init__(
            **kwargs,
            START_CODE_TAG=START_CODE_TAG,
            END_CODE_TAG=END_CODE_TAG,
            dataframes="\n\n".join(dataframes),
        )
