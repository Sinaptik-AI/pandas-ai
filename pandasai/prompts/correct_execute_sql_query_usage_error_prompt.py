from pandasai.prompts.base import BasePrompt


class CorrectExecuteSQLQueryUsageErrorPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "correct_execute_sql_query_usage_error_prompt.tmpl"
