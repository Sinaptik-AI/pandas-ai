from .base import BasePrompt


class GeneratePythonCodeWithSQLPrompt(BasePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "generate_python_code_with_sql.tmpl"
