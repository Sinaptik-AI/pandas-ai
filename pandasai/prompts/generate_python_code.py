""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

This is the initial python function. Given the context, use the right dataframes.
{current_code}

Take a deep breath and reason step-by-step. Act as a senior data analyst.
In the answer, you must never write the "technical" names of the tables.
Based on the last message in the conversation:
- return the updated analyze_data function wrapped within ```python ```"""  # noqa: E501


from .file_based_prompt import FileBasedPrompt


class CurrentCodePrompt(FileBasedPrompt):
    """The current code"""

    _path_to_template = "assets/prompt_templates/current_code.tmpl"

    def setup(self, **kwargs) -> None:
        if kwargs.get("dfs_declared", False):
            self.set_var(
                "dfs_declared_message",
                "The variable `dfs: list[pd.DataFrame]` is already declared.",
            )
        else:
            self.set_var("dfs_declared_message", "")


class SimpleReasoningPrompt(FileBasedPrompt):
    """The simple reasoning instructions"""

    _path_to_template = "assets/prompt_templates/simple_reasoning.tmpl"


class VizLibraryPrompt(FileBasedPrompt):
    """Provide information about the visualization library"""

    _path_to_template = "assets/prompt_templates/viz_library.tmpl"


class GeneratePythonCodePrompt(FileBasedPrompt):
    """Prompt to generate Python code"""

    _path_to_template = "assets/prompt_templates/generate_python_code.tmpl"

    def setup(self, **kwargs) -> None:
        self.set_var("instructions", kwargs.pop("custom_instructions", ""))

        self.set_var(
            "current_code",
            kwargs.pop("current_code", CurrentCodePrompt(dfs_declared=True)),
        )

        self.set_var(
            "code_description",
            kwargs.pop("code_description", "Update this initial code:"),
        )

        self.set_var("last_message", kwargs.pop("last_message", ""))

        self.set_var("prev_conversation", kwargs.pop("prev_conversation", ""))

    def on_prompt_generation(self) -> None:
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)
        self.set_var("reasoning", SimpleReasoningPrompt())
