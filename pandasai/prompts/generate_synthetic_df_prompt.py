from pandasai.prompts.file_based_prompt import FileBasedPrompt


class GenerateSyntheticDfPrompt(FileBasedPrompt):
    """The current code"""

    _path_to_template = "assets/prompt_templates/generate_synthetic_data.tmpl"
