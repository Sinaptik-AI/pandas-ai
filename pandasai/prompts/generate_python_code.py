""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

This is the initial python code:
{current_code}

Use the provided dataframes (`dfs`) to update the python code within the `analyze_data` function.
If the new query from the user is not relevant with the code, rewrite the content of the `analyze_data` function from scratch.
It is very important that you do not change the params that are passed to `analyze_data`.

Return the updated code:"""  # noqa: E501


from .file_based_prompt import FileBasedPrompt


class CurrentCodePrompt(FileBasedPrompt):
    """The current code"""

    _path_to_template = "assets/prompt_templates/current_code.tmpl"


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
                """Analyze the data.
If the user asks to plot a chart save it to an image in temp_chart.png and do not show the chart."""  # noqa: E501
            )

        if "current_code" in kwargs:
            self.set_var("current_code", kwargs["current_code"])
        else:
            self.set_var("current_code", CurrentCodePrompt())

    def _set_instructions(self, instructions: str):
        lines = instructions.split("\n")
        indented_lines = ["    " + line for line in lines[1:]]
        result = "\n".join([lines[0]] + indented_lines)
        self.set_var("instructions", result)
