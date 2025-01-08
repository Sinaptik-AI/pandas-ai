from .base import BasePrompt


class CorrectOutputTypeErrorPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "correct_output_type_error_prompt.tmpl"

    def to_json(self):
        context = self.props["context"]
        code = self.props["code"]
        error = self.props["error"]
        output_type = self.props["output_type"]
        memory = context.memory
        conversations = memory.to_json()

        system_prompt = memory.get_system_prompt()

        # prepare datasets
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "conversation": conversations,
            "system_prompt": system_prompt,
            "error": {
                "code": code,
                "error_trace": str(error),
                "exception_type": "InvalidLLMOutputType",
            },
            "config": {
                "direct_sql": context.config.direct_sql,
                "output_type": output_type,
            },
        }
