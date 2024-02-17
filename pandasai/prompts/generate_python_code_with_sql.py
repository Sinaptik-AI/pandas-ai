from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class GeneratePythonCodeWithSQLPrompt(GeneratePythonCodePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "generate_python_code_with_sql.tmpl"
