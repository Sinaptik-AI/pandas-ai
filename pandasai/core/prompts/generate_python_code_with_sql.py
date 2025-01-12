from .base import BasePrompt


class GeneratePythonCodeWithSQLPrompt(BasePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "generate_python_code_with_sql.tmpl"

    def to_json(self):
        context = self.props["context"]
        output_type = self.props["output_type"]
        memory = context.memory
        conversations = memory.to_json()

        system_prompt = memory.agent_description

        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "conversation": conversations,
            "system_prompt": system_prompt,
            "prompt": self.to_string(),
            "config": {
                "direct_sql": context.config.direct_sql,
                "output_type": output_type,
            },
        }
