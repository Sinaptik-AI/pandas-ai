""" Prompt to explain code generation by the LLM
The previous conversation we had

<Conversation>
{conversation}
</Conversation>

Based on the last conversation you generated the following code:

<Code>
{code}
</Code>

Explain how you came up with code for non-technical people without 
mentioning technical details or mentioning the libraries used?

"""
from .file_based_prompt import FileBasedPrompt


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

    def setup(self, tables) -> None:
        self.set_var("tables", self._prepare_tables_data(tables))
