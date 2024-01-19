""" Prompt to explain code generation by the LLM"""
from .generate_python_code import (
    CurrentCodePrompt,
    GeneratePythonCodePrompt,
    SimpleReasoningPrompt,
)


class DirectSQLPrompt(GeneratePythonCodePrompt):
    """Prompt to explain code generation by the LLM"""

    _path_to_template = "assets/prompt_templates/direct_sql_connector.tmpl"

    def _prepare_tables_data(self, tables):
        tables_join = []
        for table in tables:
            table_description_tag = (
                f' description="{table.description}"'
                if table.description is not None
                else ""
            )
            table_head_tag = f'<table name="{table.name}"{table_description_tag}>'
            table = f"{table_head_tag}\n{table.to_csv()}\n</table>"
            tables_join.append(table)
        return "\n\n".join(tables_join)

    def setup(self, tables, **kwargs) -> None:
        self.set_var("tables", self._prepare_tables_data(tables))

        super(DirectSQLPrompt, self).setup(**kwargs)

        self.set_var("current_code", kwargs.pop("current_code", CurrentCodePrompt()))
        self.set_var(
            "code_description",
            kwargs.pop("code_description", "Update this initial code:"),
        )
        self.set_var("last_message", kwargs.pop("last_message", ""))
        self.set_var("prev_conversation", kwargs.pop("prev_conversation", ""))

    def on_prompt_generation(self) -> None:
        default_import = "import pandas as pd"

        self.set_var("default_import", default_import)
        self.set_var("reasoning", SimpleReasoningPrompt())
