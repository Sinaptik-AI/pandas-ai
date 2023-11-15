""" Prompt to correct Python Code on Error
```
{dataframes}

{conversation}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Fix the python code above and return the new python code:
"""  # noqa: E501

from .file_based_prompt import FileBasedPrompt


class CorrectErrorPrompt(FileBasedPrompt):
    """Prompt to Correct Python code on Error"""

    _path_to_template = "assets/prompt_templates/correct_error_prompt.tmpl"
