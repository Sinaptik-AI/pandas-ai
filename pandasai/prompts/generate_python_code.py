""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames with the following metadata:

{dataframes}

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
{default_import}

# Analyze the data
# 1. Prepare: Preprocessing and cleaning data if necessary
# 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
# 3. Analyze: Conducting the actual analysis (if the user asks to create a chart save it to an image in exports/charts/temp_chart.png and do not show the chart.)
# 4. Output: return a dictionary of:
# - type (possible values "text", "number", "dataframe", "plot")
# - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
# Example output: {{ "type": "text", "value": "The average loan amount is $15,000." }}
def analyze_data(dfs: list[{engine_df_name}]) -> dict:
    # Code goes here (do not add comments)


# Declare a result variable
result = analyze_data(dfs)
```

Using the provided dataframes (`dfs`), update the python code based on the last user question:
{conversation}

Updated code:
"""  # noqa: E501


from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
You are provided with the following pandas DataFrames with the following metadata:

{dataframes}

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
{default_import}

# Analyze the data
# 1. Prepare: Preprocessing and cleaning data if necessary
# 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
# 3. Analyze: Conducting the actual analysis (if the user asks to create a chart save it to an image in exports/charts/temp_chart.png and do not show the chart.)
# 4. Output: return a dictionary of:
# - type (possible values "text", "number", "dataframe", "plot")
# - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
# Example output: {{ "type": "text", "value": "The average loan amount is $15,000." }}
def analyze_data(dfs: list[{engine_df_name}]) -> dict:
   # Code goes here (do not add comments)
    

# Declare a result variable
result = analyze_data(dfs)
```

Using the provided dataframes (`dfs`), update the python code based on the last user question:
{conversation}

Updated code:
"""  # noqa: E501

    def __init__(self):
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)
