""" Prompt to explain code generation by the LLM"""
from .file_based_prompt import FileBasedPrompt
from .generate_python_code import (
    CurrentCodePrompt,
    SimpleReasoningPrompt,
    DefaultInstructionsPrompt,
)


class DirectSQLPrompt(FileBasedPrompt):
    """Prompt to explain code generation by the LLM"""

    _path_to_template = "assets/prompt_templates/direct_sql_connector.tmpl"

    def _prepare_tables_data(self, tables):
        tables_join = []
        for table in tables:
            table_description_tag = (
                f' description="{table.table_description}"'
                if table.table_description is not None
                else ""
            )
            table_head_tag = f'<table name="{table.table_name}"{table_description_tag}>'
            table = f"{table_head_tag}\n{table.head_csv}\n</table>"
            tables_join.append(table)
        return "\n\n".join(tables_join)

    def setup(self, tables, **kwargs) -> None:
        self.set_var("tables", self._prepare_tables_data(tables))

        if "custom_instructions" in kwargs:
            self.set_var("instructions", kwargs["custom_instructions"])
        else:
            self.set_var("instructions", DefaultInstructionsPrompt())

        if "current_code" in kwargs:
            self.set_var("current_code", kwargs["current_code"])
        else:
            self.set_var("current_code", CurrentCodePrompt())

        if "code_description" in kwargs:
            self.set_var("code_description", kwargs["code_description"])
        else:
            self.set_var("code_description", "Update this initial code:")

        if "last_message" in kwargs:
            self.set_var("last_message", kwargs["last_message"])
        else:
            self.set_var("last_message", "")

        if "prev_conversation" in kwargs:
            self.set_var("prev_conversation", kwargs["prev_conversation"])
        else:
            self.set_var("prev_conversation", "")

    def on_prompt_generation(self) -> None:
        default_import = "import pandas as pd"
        engine_df_name = "pd.DataFrame"

        self.set_var("default_import", default_import)
        self.set_var("engine_df_name", engine_df_name)
        self.set_var("reasoning", SimpleReasoningPrompt())
