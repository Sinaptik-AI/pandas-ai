""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
{default_import}

def analyze_data(dfs: list[{engine_df_name}]) -> dict:
    \"\"\"
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in {save_charts_path}/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    - type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Example output: {{ "type": "text", "value": "The average loan amount is $15,000." }}
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.
{conversation}

Updated code:
"""  # noqa: E501


from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
{default_import}

def analyze_data(dfs: list[{engine_df_name}]) -> dict:
    \"\"\"
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in {save_charts_path}/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    {output_type_hint}
    Example output: {{ "type": "text", "value": "The average loan amount is $15,000." }}
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.

Updated code:
"""  # noqa: E501
    _output_type_map = {
        "number": """- type (must be "number")
    - value (must be a number)""",
        "dataframe": """- type (must be "dataframe")
    - value (must be a pandas dataframe)""",
        "plot": """- type (must be "plot")
    - value (must be a string containing the path of the plot image)""",
        "string": """- type (must be "string")
    - value (must be a conversational answer, as a string)""",
    }
    _output_type_default = """- type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)"""  # noqa E501

    def __init__(self):
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)

    @classmethod
    def get_output_type_hint(cls, output_type):
        return cls._output_type_map.get(output_type, cls._output_type_default)
