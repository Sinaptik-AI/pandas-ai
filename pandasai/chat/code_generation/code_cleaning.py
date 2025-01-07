import ast
import copy
import re
from typing import Union

import astor
from pandasai.agent.state import AgentState

from pandasai.chat.code_execution.code_executor import CodeExecutor
from pandasai.helpers.path import find_project_root
from pandasai.helpers.sql import extract_table_names

from ...constants import WHITELISTED_LIBRARIES
from ...exceptions import BadImportError, MaliciousQueryError
from ...helpers.save_chart import add_save_chart


class CodeCleaner:
    def __init__(self, context: AgentState):
        """
        Initialize the CodeCleaner with the provided context.

        Args:
            context (AgentState): The pipeline context for cleaning and validation.
        """
        self.context = context

    def _check_imports(self, node: Union[ast.Import, ast.ImportFrom]):
        """
        Add whitelisted imports to _additional_dependencies.

        Args:
            node (object): ast.Import or ast.ImportFrom

        Raises:
            BadImportError: If the import is not whitelisted

        """
        module = node.names[0].name if isinstance(node, ast.Import) else node.module
        library = module.split(".")[0]

        if library == "pandas":
            return

        whitelisted_libs = (
            WHITELISTED_LIBRARIES + self._config.custom_whitelisted_dependencies
        )

        if library not in whitelisted_libs:
            raise BadImportError(
                f"The library '{library}' is not in the list of whitelisted libraries. "
                "To learn how to whitelist custom dependencies, visit: "
                "https://docs.pandas-ai.com/custom-whitelisted-dependencies#custom-whitelisted-dependencies"
            )

        for alias in node.names:
            return {
                "module": module,
                "name": alias.name,
                "alias": alias.asname or alias.name,
            }

    def _check_is_df_declaration(self, node: ast.AST) -> bool:
        """
        Check if the node represents a pandas DataFrame declaration.
        """
        value = node.value
        return (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and isinstance(value.func.value, ast.Name)
            and hasattr(value.func.value, "id")
            and value.func.value.id == "pd"
            and value.func.attr == "DataFrame"
        )

    def _get_target_names(self, targets):
        """
        Extract target names from AST nodes.
        """
        target_names = []
        is_slice = False

        for target in targets:
            if isinstance(target, ast.Name) or (
                isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
            ):
                target_names.append(
                    target.id if isinstance(target, ast.Name) else target.value.id
                )
                is_slice = isinstance(target, ast.Subscript)

        return target_names, is_slice, target

    def _check_direct_sql_func_def_exists(self, node: ast.AST) -> bool:
        """
        Check if the node defines a direct SQL execution function.
        """
        return (
            self.context.config.direct_sql
            and isinstance(node, ast.FunctionDef)
            and node.name == "execute_sql_query"
        )

    def _replace_table_names(
        self, sql_query: str, table_names: list, allowed_table_names: list
    ) -> str:
        """
        Replace table names in the SQL query with case-sensitive or authorized table names.
        """
        regex_patterns = {
            table_name: re.compile(r"\b" + re.escape(table_name) + r"\b")
            for table_name in table_names
        }
        for table_name in table_names:
            if table_name in allowed_table_names:
                quoted_table_name = allowed_table_names[table_name]
                sql_query = regex_patterns[table_name].sub(quoted_table_name, sql_query)
            else:
                raise MaliciousQueryError(
                    f"Query uses unauthorized table: {table_name}."
                )
        return sql_query

    def _clean_sql_query(self, sql_query: str) -> str:
        """
        Clean the SQL query by trimming semicolons and validating table names.
        """
        sql_query = sql_query.rstrip(";")
        table_names = extract_table_names(sql_query)
        allowed_table_names = {df.name: df.name for df in self.context.dfs} | {
            f'"{df.name}"': df.name for df in self.context.dfs
        }
        return self._replace_table_names(sql_query, table_names, allowed_table_names)

    def _validate_and_make_table_name_case_sensitive(self, node: ast.AST) -> ast.AST:
        """
        Validate table names and convert them to case-sensitive names in the SQL query.
        """
        if isinstance(node, ast.Assign):
            if (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ["sql_query", "query"]
            ):
                sql_query = self._clean_sql_query(node.value.value)
                node.value.value = sql_query
            elif (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "execute_sql_query"
                and len(node.value.args) == 1
                and isinstance(node.value.args[0], ast.Constant)
                and isinstance(node.value.args[0].value, str)
            ):
                sql_query = self._clean_sql_query(node.value.args[0].value)
                node.value.args[0].value = sql_query

        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id == "execute_sql_query"
                and len(node.value.args) == 1
                and isinstance(node.value.args[0], ast.Constant)
                and isinstance(node.value.args[0].value, str)
            ):
                sql_query = self._clean_sql_query(node.value.args[0].value)
                node.value.args[0].value = sql_query

        return node

    def extract_fix_dataframe_redeclarations(
        self,
        node: ast.AST,
        code_lines: list[str],
        additional_deps: list[dict],
    ) -> ast.AST:
        """
        Checks if dataframe reclaration in the code like pd.DataFrame({...})
        Args:
            node (ast.AST): Code Node
            code_lines (list[str]): List of code str line by line

        Returns:
            ast.AST: Updated Ast Node fixing redeclaration
        """
        if isinstance(node, ast.Assign):
            target_names, is_slice, target = self.get_target_names(node.targets)

            if target_names and self.check_is_df_declaration(node):
                # Construct dataframe from node
                code = "\n".join(code_lines)
                code_executor = CodeExecutor(additional_deps)
                code_executor.add_to_env("dfs", copy.deepcopy(self.context.dfs))
                env = code_executor.execute(code)

                df_generated = (
                    env[target_names[0]][target.slice.value]
                    if is_slice
                    else env[target_names[0]]
                )

                # check if exists in provided dfs
                for index, df in enumerate(self.context.dfs):
                    head = df.get_head()
                    if head.shape == df_generated.shape and head.columns.equals(
                        df_generated.columns
                    ):
                        target_var = (
                            ast.Subscript(
                                value=ast.Name(id=target_names[0], ctx=ast.Load()),
                                slice=target.slice,
                                ctx=ast.Store(),
                            )
                            if is_slice
                            else ast.Name(id=target_names[0], ctx=ast.Store())
                        )
                        return ast.Assign(
                            targets=[target_var],
                            value=ast.Subscript(
                                value=ast.Name(id="dfs", ctx=ast.Load()),
                                slice=ast.Index(value=ast.Num(n=index)),
                                ctx=ast.Load(),
                            ),
                        )
        return None

    def get_target_names(self, targets):
        target_names = []
        is_slice = False

        for target in targets:
            if isinstance(target, ast.Name) or (
                isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
            ):
                target_names.append(
                    target.id if isinstance(target, ast.Name) else target.value.id
                )
                is_slice = isinstance(target, ast.Subscript)

        return target_names, is_slice, target

    def check_is_df_declaration(self, node: ast.AST):
        value = node.value
        return (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and isinstance(value.func.value, ast.Name)
            and hasattr(value.func.value, "id")
            and value.func.value.id == "pd"
            and value.func.attr == "DataFrame"
        )

    def clean_code(self, code: str) -> tuple[str, list]:
        """
        Clean the provided code by validating imports, handling SQL queries, and processing charts.

        Args:
            code (str): The code to clean.

        Returns:
            tuple: Cleaned code as a string and a list of additional dependencies.
        """
        code = self._handle_charts(code)

        # If plt.show is in the code, remove that line
        code = re.sub(r"plt.show\(\)", "", code)

        additional_dependencies = []
        clean_code_lines = []

        tree = ast.parse(code)
        new_body = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported_lib = self._check_imports(node)
                if imported_lib:
                    additional_dependencies.append(imported_lib)
                continue

            if self._check_direct_sql_func_def_exists(node):
                continue

            if self.context.config.direct_sql:
                node = self._validate_and_make_table_name_case_sensitive(node)

            clean_code_lines.append(astor.to_source(node))

            new_body.append(
                self.extract_fix_dataframe_redeclarations(
                    node, clean_code_lines, additional_dependencies
                )
                or node
            )

        new_tree = ast.Module(body=new_body)
        return (
            astor.to_source(new_tree, pretty_source=lambda x: "".join(x)).strip(),
            additional_dependencies,
        )

    def _handle_charts(self, code: str) -> str:
        """
        Handle chart-related code modifications.
        """
        code = re.sub(r"""(['"])([^'"]*\.png)\1""", r"\1temp_chart.png\1", code)
        if self.context.config.save_charts:
            return add_save_chart(
                code,
                logger=self.context.logger,
                file_name=str(self.context.prompt_id),
                save_charts_path_str=self.context.config.save_charts_path,
            )
        return add_save_chart(
            code,
            logger=self.context.logger,
            file_name="temp_chart",
            save_charts_path_str=f"{find_project_root()}/exports/charts",
        )
