from pandasai.core.prompts.base import BasePrompt


class CorrectExecuteSQLQueryUsageErrorPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "correct_execute_sql_query_usage_error_prompt.tmpl"

    def to_json(self):
        context = self.props["context"]
        code = self.props["code"]
        error = self.props["error"]
        memory = context.memory
        conversations = memory.to_json()

        system_prompt = memory.agent_description

        # prepare datasets
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "conversation": conversations,
            "system_prompt": system_prompt,
            "error": {
                "code": code,
                "error_trace": str(error),
                "exception_type": "ExecuteSQLQueryNotUsed",
            },
        }
