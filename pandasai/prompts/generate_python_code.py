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
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in temp_chart.png and do not show the chart.)
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


from .base import FileBasedPrompt


class GeneratePythonCodePrompt(FileBasedPrompt):
    """Prompt to generate Python code"""

    _path_to_template = "assets/prompt-templates/generate_python_code.tmpl"

    def __init__(self, **kwargs):
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)

        super().__init__(**kwargs)
