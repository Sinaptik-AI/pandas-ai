""" Prompt to correct Python Code on Error
```
You are provided with the following pandas DataFrames with the following metadata:

{dataframes}

The user asked the following question:
{conversation}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code that fixes the above mentioned error. Do not generate the same code again.
"""  # noqa: E501

from .file_based_prompt import FileBasedPrompt


class CorrectErrorPrompt(FileBasedPrompt):
    """Prompt to Correct Python code on Error"""

    _path_to_template = "assets/prompt_templates/correct_error_prompt.tmpl"
