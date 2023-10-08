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
    At the end, return a dictionary of:
    - type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Example output: {{ "type": "string", "value": f"The average loan amount is {{average_amount}}" }}
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.
{conversation}

Updated code:
"""  # noqa: E501


from .file_based_prompt import FileBasedPrompt


class GeneratePythonCodePrompt(FileBasedPrompt):
    """Prompt to generate Python code"""

    _path_to_template = "assets/prompt_templates/generate_python_code.tmpl"

    def setup(self, **kwargs) -> None:
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)

        if "custom_instructions" in kwargs:
            self._set_instructions(kwargs["custom_instructions"])
        else:
            self._set_instructions(
                """Analyze the data
1. Prepare: Preprocessing and cleaning data if necessary
2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in temp_chart.png and do not show the chart.)"""  # noqa: E501
            )

    def _set_instructions(self, instructions: str):
        lines = instructions.split("\n")
        indented_lines = ["    " + line for line in lines[1:]]
        result = "\n".join([lines[0]] + indented_lines)
        self.set_var("instructions", result)
