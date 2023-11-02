""" Prompt to generate Python code
```
You are provided with the following pandas DataFrames:

{dataframes}

<conversation>
{conversation}
</conversation>

This is the initial python function. Do not change the params. Given the context, use the right dataframes.
{current_code}

Take a deep breath and reason step-by-step. Act as a senior data analyst.
In the answer, you must never write the "technical" names of the tables.
Based on the last message in the conversation:
- return the updated analyze_data function wrapped within ```python ```"""  # noqa: E501


from .file_based_prompt import FileBasedPrompt


class CurrentCodePrompt(FileBasedPrompt):
    """The current code"""

    _path_to_template = "assets/prompt_templates/current_code.tmpl"


class DefaultInstructionsPrompt(FileBasedPrompt):
    """The default instructions"""

    _path_to_template = "assets/prompt_templates/default_instructions.tmpl"


class AdvancedReasoningPrompt(FileBasedPrompt):
    """The advanced reasoning instructions"""

    _path_to_template = "assets/prompt_templates/advanced_reasoning.tmpl"


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
        if "custom_instructions" in kwargs:
            self.set_var(
                "instructions", self._format_instructions(kwargs["custom_instructions"])
            )
        else:
            self.set_var("instructions", DefaultInstructionsPrompt())

        if "current_code" in kwargs:
            self.set_var("current_code", kwargs["current_code"])
        else:
            self.set_var("current_code", CurrentCodePrompt())

    def on_prompt_generation(self) -> None:
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)
        if self.get_config("use_advanced_reasoning_framework"):
            self.set_var("reasoning", AdvancedReasoningPrompt())
        else:
            self.set_var("reasoning", SimpleReasoningPrompt())

    def _format_instructions(self, instructions: str):
        lines = instructions.split("\n")
        indented_lines = [f"    {line}" for line in lines[1:]]
        result = "\n".join([lines[0]] + indented_lines)
        return result
