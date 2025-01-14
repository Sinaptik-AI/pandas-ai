import ast
import os
import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError


class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # Setup a mock context for CodeCleaner
        self.context = MagicMock(spec=AgentState)
        self.cleaner = CodeCleaner(self.context)
        self.sample_df = DataFrame(
            {
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [6.94, 7.22, 5.87, 5.12],
            }
        )

    def test_check_direct_sql_func_def_exists_true(self):
        node = ast.FunctionDef(
            name="execute_sql_query",
            args=ast.arguments(
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[],
            decorator_list=[],
            returns=None,
        )
        result = self.cleaner._check_direct_sql_func_def_exists(node)
        self.assertTrue(result)

    def test_replace_table_names_valid(self):
        sql_query = "SELECT * FROM my_table;"
        table_names = ["my_table"]
        allowed_table_names = {"my_table": "my_table"}
        result = self.cleaner._replace_table_names(
            sql_query, table_names, allowed_table_names
        )
        self.assertEqual(result, "SELECT * FROM my_table;")

    def test_replace_table_names_invalid(self):
        sql_query = "SELECT * FROM my_table;"
        table_names = ["my_table"]
        allowed_table_names = {}
        with self.assertRaises(MaliciousQueryError):
            self.cleaner._replace_table_names(
                sql_query, table_names, allowed_table_names
            )

    def test_clean_sql_query(self):
        sql_query = "SELECT * FROM my_table;"
        mock_dataframe = MagicMock(spec=object)
        mock_dataframe.name = "my_table"
        self.cleaner.context.dfs = [mock_dataframe]
        result = self.cleaner._clean_sql_query(sql_query)
        self.assertEqual(result, "SELECT * FROM my_table")

    def test_validate_and_make_table_name_case_sensitive(self):
        node = ast.Assign(
            targets=[ast.Name(id="query", ctx=ast.Store())],
            value=ast.Constant(value="SELECT * FROM my_table"),
        )
        mock_dataframe = MagicMock(spec=object)
        mock_dataframe.name = "my_table"
        self.cleaner.context.dfs = [mock_dataframe]
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        self.assertEqual(updated_node.value.value, "SELECT * FROM my_table")

    def test_extract_fix_dataframe_redeclarations(self):
        node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="DataFrame",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.cleaner.context.dfs = [self.sample_df]
        code_lines = [
            """df = pd.DataFrame({
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [6.94, 7.22, 5.87, 5.12],
            })"""
        ]
        updated_node = self.cleaner.extract_fix_dataframe_redeclarations(
            node, code_lines
        )
        self.assertIsInstance(updated_node, ast.AST)

    def test_replace_output_filenames_with_temp_chart(self):
        handler = self.cleaner
        handler.context = MagicMock()
        handler.context.config.save_charts = True
        handler.context.logger = MagicMock()  # Mock logger
        handler.context.last_prompt_id = 123
        handler.context.config.save_charts_path = "/custom/path"

        code = 'some text "hello.png" more text'

        code = handler._replace_output_filenames_with_temp_chart(code)

        expected_code = f'some text "{os.path.join("exports", "charts", "temp_chart.png")}" more text'
        self.assertEqual(code, expected_code)

    def test_replace_output_filenames_with_temp_chart_empty_code(self):
        handler = self.cleaner

        code = ""
        expected_code = ""  # It should remain empty, as no substitution is made

        result = handler._replace_output_filenames_with_temp_chart(code)

        self.assertEqual(
            result, expected_code, f"Expected '{expected_code}', but got '{result}'"
        )

    def test_replace_output_filenames_with_temp_chart_no_png(self):
        handler = self.cleaner

        code = "some text without png"
        expected_code = "some text without png"  # No change should occur

        result = handler._replace_output_filenames_with_temp_chart(code)

        self.assertEqual(
            result, expected_code, f"Expected '{expected_code}', but got '{result}'"
        )


if __name__ == "__main__":
    unittest.main()
