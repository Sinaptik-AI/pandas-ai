""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

```python
# TODO import all the dependencies required
{default_import}

def analyze_data(dfs: list[{engine_df_name}]) -> dict:
    \"\"\"
    Analyze the data
    If the user asks to plot a chart save it to an image in temp_chart.png and do not show the chart.
    At the end, return a dictionary of:
    - type (possible values "string", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Examples: 
        { "type": "string", "value": "The highest salary is $9,000." }
        or
        { "type": "number", "value": 125 }
        or
        { "type": "dataframe", "value": pd.DataFrame({...}) }
        or
        { "type": "plot", "value": "temp_chart.png" }
    \"\"\"
```

Use the provided dataframes (`dfs`) and update the python code to answer the last question in the conversation.

Return the updated code:"""  # noqa: E501


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
If the user asks to plot a chart save it to an image in temp_chart.png and do not show the chart."""  # noqa: E501
            )

    def _set_instructions(self, instructions: str):
        lines = instructions.split("\n")
        indented_lines = ["    " + line for line in lines[1:]]
        result = "\n".join([lines[0]] + indented_lines)
        self.set_var("instructions", result)
