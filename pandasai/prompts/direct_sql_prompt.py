""" Prompt to explain code generation by the LLM"""
import pandasai.pandas as pd
from pandasai.helpers.dataframe_serializer import (
    DataframeSerializer,
    DataframeSerializerType,
)

from .generate_python_code import (
    CurrentCodePrompt,
    GeneratePythonCodePrompt,
    SimpleReasoningPrompt,
)


class DirectSQLPrompt(GeneratePythonCodePrompt):
    """Prompt to explain code generation by the LLM"""

    _path_to_template = "assets/prompt_templates/direct_sql_connector.tmpl"

    def _prepare_tables_data(self, tables, config):
        tables_join = []
        for index, table in enumerate(tables):
            table_serialized = DataframeSerializer().serialize(
                table,
                {
                    "index": index,
                    "type": "sql" if config and config.direct_sql else "pandas",
                },
                (
                    config.dataframe_serializer
                    if config
                    else DataframeSerializerType.SQL
                ),
            )
            tables_join.append(table_serialized)
        return "\n\n".join(tables_join)

    def setup(self, tables, config=None, **kwargs) -> None:
        self.set_var("tables", self._prepare_tables_data(tables, config))

        super(DirectSQLPrompt, self).setup(**kwargs)

        self.set_var("current_code", kwargs.pop("current_code", CurrentCodePrompt()))
        self.set_var(
            "code_description",
            kwargs.pop("code_description", "Update this initial code:"),
        )
        self.set_var("last_message", kwargs.pop("last_message", ""))
        self.set_var("prev_conversation", kwargs.pop("prev_conversation", ""))

    def on_prompt_generation(self) -> None:
        default_import = f"import {pd.__name__} as pd"

        self.set_var("default_import", default_import)
        self.set_var("reasoning", SimpleReasoningPrompt())
