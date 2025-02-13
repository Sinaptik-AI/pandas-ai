import ast
import os
import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import astor
import pandas as pd
import pytest

from pandasai.agent.state import AgentState
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.core.code_execution.code_executor import CodeExecutor
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError


class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # Set up a sample DataFrame with consistent data for testing.
        sample_data = {
            "country": ["United States", "United Kingdom", "Japan", "China"],
            "gdp": [19294482071552, 2891615567872, 4380756541440, 14631844184064],
            "happiness_index": [6.94, 7.22, 5.87, 5.12],
        }
        self.sample_df = DataFrame(sample_data)
        # For tests expecting a schema attribute, assign a dummy schema with a name.
        self.sample_df.schema = type("DummySchema", (), {})()
        self.sample_df.schema.name = "sample_table"
        # Initialize AgentState with the list of dataframes.
        state = AgentState(dfs=[self.sample_df])
        self.cleaner = CodeCleaner(state)

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
        table = self.sample_df.schema.name
        sql_query = f"SELECT * FROM {table};"
        self.cleaner.context.dfs = [self.sample_df]
        result = self.cleaner._clean_sql_query(sql_query)
        self.assertEqual(result, f"SELECT * FROM {table}")

    def test_validate_and_make_table_name_case_sensitive(self):
        table = self.sample_df.schema.name
        node = ast.Assign(
            targets=[ast.Name(id="query", ctx=ast.Store())],
            value=ast.Constant(value=f"SELECT * FROM {table}"),
        )
        self.cleaner.context.dfs = [self.sample_df]
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        self.assertEqual(updated_node.value.value, f"SELECT * FROM {table}")

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
        expected_code = ""
        result = handler._replace_output_filenames_with_temp_chart(code)
        self.assertEqual(
            result, expected_code, f"Expected '{expected_code}', but got '{result}'"
        )

    def test_replace_output_filenames_with_temp_chart_no_png(self):
        handler = self.cleaner
        code = "some text without png"
        expected_code = "some text without png"
        result = handler._replace_output_filenames_with_temp_chart(code)
        self.assertEqual(
            result, expected_code, f"Expected '{expected_code}', but got '{result}'"
        )

    def test_clean_code_full_cleaning(self):
        """
        Test that clean_code properly cleans the entire code by:
        - Removing the 'execute_sql_query' function definition.
        - Removing 'plt.show()' calls.
        - Replacing PNG filenames with the temporary chart path.
        - Cleaning SQL queries by removing trailing semicolons.
        - Fixing DataFrame redeclarations by replacing them with a reference to dfs.
        """
        self.cleaner.context.dfs = [self.sample_df]
        table = self.sample_df.schema.name
        code = (
            "def execute_sql_query(query):\n"
            "    return query\n\n"
            f'query = "SELECT * FROM {table};"\n'
            "df = pd.DataFrame({"
            '"country": ["United States", "United Kingdom", "Japan", "China"],'
            '"gdp": [19294482071552,2891615567872,4380756541440,14631844184064],'
            '"happiness_index": [6.94,7.22,5.87,5.12]'
            "})\n"
            'print("Saving to output.png")\n'
            "plt.show()\n"
        )
        sample_df = self.sample_df

        def mocked_execute(executor, code_str):
            return {"df": sample_df}

        with patch.object(CodeExecutor, "execute", new=mocked_execute):
            cleaned_code = self.cleaner.clean_code(code)
        self.assertNotIn("def execute_sql_query", cleaned_code)
        self.assertNotIn("plt.show()", cleaned_code)
        # Normalize paths by replacing both single and double backslashes with forward slashes
        cleaned_code_normalized = re.sub(r"\\+", "/", cleaned_code)
        expected_png_path = str(
            Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png"
        ).replace("\\", "/")
        self.assertIn(expected_png_path, cleaned_code_normalized)
        self.assertNotIn(";", cleaned_code)
        self.assertIn("dfs[0]", cleaned_code)

    def test_get_target_names_empty_and_valid(self):
        """
        Test the get_target_names method for a valid list of targets and for an empty targets list.
        For the non-empty case, we verify that the names are collected correctly and the is_slice flag is set
        based on the last target. For an empty list, we expect an UnboundLocalError.
        """
        self.cleaner.context = MagicMock()
        # Test with a valid list of targets: one ast.Name followed by an ast.Subscript.
        name_node = ast.Name(id="a", ctx=ast.Store())
        subscript_node = ast.Subscript(
            value=ast.Name(id="b", ctx=ast.Load()),
            slice=ast.Index(value=ast.Constant(value=1)),
            ctx=ast.Store(),
        )
        targets = [name_node, subscript_node]
        names, is_slice, last_target = self.cleaner.get_target_names(targets)
        self.assertEqual(names, ["a", "b"])
        self.assertTrue(is_slice)
        self.assertEqual(last_target, subscript_node)
        # Test with an empty list of targets.
        with self.assertRaises(UnboundLocalError):
            self.cleaner.get_target_names([])

    def test_validate_and_make_table_name_case_sensitive_expr(self):
        """
        Test that SQL queries passed via execute_sql_query in expression statements are cleaned properly
        (i.e. trailing semicolons are removed).
        """
        table = self.sample_df.schema.name
        self.cleaner.context.dfs = [self.sample_df]
        expr_node = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
                args=[ast.Constant(value=f"SELECT * FROM {table};")],
                keywords=[],
            )
        )
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(
            expr_node
        )
        self.assertEqual(updated_node.value.args[0].value, f"SELECT * FROM {table}")

    def test_validate_and_make_table_name_case_sensitive_no_change(self):
        """
        Test that _validate_and_make_table_name_case_sensitive leaves nodes unchanged
        when they do not match any criteria for SQL query cleaning.
        """
        node = ast.Expr(value=ast.Constant(value=42))
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        self.assertIs(updated_node, node)

    def test_extract_fix_dataframe_redeclarations_no_match(self):
        """
        Test that extract_fix_dataframe_redeclarations returns None when the pd.DataFrame redeclaration
        does not match any dataframe provided in the context.
        """
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
        code_lines = [
            """df = pd.DataFrame({
                "different_col": [1, 2, 3]
            })"""
        ]
        self.cleaner.context.dfs = [self.sample_df]
        mismatch_df = DataFrame({"different_col": [1, 2, 3]})

        def fake_execute(executor, code_str):
            return {"df": mismatch_df}

        with patch.object(CodeExecutor, "execute", new=fake_execute):
            updated_node = self.cleaner.extract_fix_dataframe_redeclarations(
                node, code_lines
            )
        self.assertIsNone(updated_node)

    def test_check_is_df_declaration(self):
        """
        Test that check_is_df_declaration correctly identifies an AST node representing a pd.DataFrame call.
        It also ensures that nodes not representing a pd.DataFrame call return False.
        """
        valid_df_node = ast.Assign(
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
        self.assertTrue(
            self.cleaner.check_is_df_declaration(valid_df_node),
            "Expected check_is_df_declaration to return True for a valid pd.DataFrame call.",
        )
        invalid_df_node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="numpy", ctx=ast.Load()),
                    attr="DataFrame",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.assertFalse(
            self.cleaner.check_is_df_declaration(invalid_df_node),
            "Expected check_is_df_declaration to return False when not using pd.",
        )

    def test_clean_code_empty(self):
        """
        Test that clean_code properly handles an empty code string and returns an empty string.
        """
        result = self.cleaner.clean_code("")
        self.assertEqual(result.strip(), "")

    def test_clean_sql_query(self):
        """
        Test that _clean_sql_query correctly cleans a SQL query containing multiple occurrences
        of an allowed table name, and removes the trailing semicolon.
        """
        self.cleaner.context.dfs = [self.sample_df]
        table = self.sample_df.schema.name
        sql_query = f"SELECT * FROM {table} JOIN {table};"
        cleaned_query = self.cleaner._clean_sql_query(sql_query)
        expected_query = f"SELECT * FROM {table} JOIN {table}"
        self.assertEqual(cleaned_query, expected_query)

    def test_extract_fix_dataframe_redeclarations_with_subscript(self):
        """
        Test that extract_fix_dataframe_redeclarations correctly processes a DataFrame
        redeclaration when the target is a subscript (e.g. df[0]), replacing it with
        a reference to dfs at the corresponding index.
        """
        subscript_target = ast.Subscript(
            value=ast.Name(id="df", ctx=ast.Load()),
            slice=ast.Index(value=ast.Constant(value=0)),
            ctx=ast.Store(),
        )
        node = ast.Assign(
            targets=[subscript_target],
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
        code_lines = [
            """df = pd.DataFrame({
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [19294482071552,2891615567872,4380756541440,14631844184064],
                "happiness_index": [6.94,7.22,5.87,5.12]
            })"""
        ]
        self.cleaner.context.dfs = [self.sample_df]

        def fake_execute(executor, code_str):
            return {"df": [self.sample_df]}

        with patch.object(CodeExecutor, "execute", new=fake_execute):
            updated_node = self.cleaner.extract_fix_dataframe_redeclarations(
                node, code_lines
            )
        self.assertIsNotNone(updated_node)
        self.assertIsInstance(updated_node, ast.Assign)
        self.assertTrue(isinstance(updated_node.targets[0], ast.Subscript))
        target_node = updated_node.targets[0]
        self.assertEqual(target_node.value.id, "df")
        self.assertIsInstance(updated_node.value, ast.Subscript)
        self.assertEqual(updated_node.value.value.id, "dfs")
        index_value = None
        if isinstance(updated_node.value.slice, ast.Index):
            if hasattr(updated_node.value.slice.value, "n"):
                index_value = updated_node.value.slice.value.n
            elif hasattr(updated_node.value.slice.value, "value"):
                index_value = updated_node.value.slice.value.value
        else:
            if hasattr(updated_node.value.slice, "n"):
                index_value = updated_node.value.slice.n
            elif hasattr(updated_node.value.slice, "value"):
                index_value = updated_node.value.slice.value
        self.assertEqual(index_value, 0)


if __name__ == "__main__":
    unittest.main()

    def test_clean_sql_query_with_quoted_table(self):
        """
        Test that _clean_sql_query correctly cleans an SQL query that contains a quoted table name.
        The test ensures that a table referenced as "sample_table" is replaced with sample_table
        and that the trailing semicolon is removed.
        """
        table = self.sample_df.schema.name
        query = f'SELECT * FROM "{table}";'
        self.cleaner.context.dfs = [self.sample_df]
        cleaned_query = self.cleaner._clean_sql_query(query)
        expected_query = f"SELECT * FROM {table}"
        self.assertEqual(cleaned_query, expected_query)

    def test_clean_sql_query_multiple_trailing_semicolons(self):
        """
        Test that _clean_sql_query correctly removes multiple trailing semicolons from the SQL query
        and replaces table names with the allowed names.
        """
        table = self.sample_df.schema.name
        # Create a query with multiple trailing semicolons.
        sql_query = f"SELECT * FROM {table};;;"
        self.cleaner.context.dfs = [self.sample_df]
        cleaned_query = self.cleaner._clean_sql_query(sql_query)
        # Expect that all the trailing semicolons have been removed.
        self.assertEqual(cleaned_query, f"SELECT * FROM {table}")

    def test_replace_output_filenames_with_temp_chart_single_quotes(self):
        """
        Test that _replace_output_filenames_with_temp_chart correctly replaces png filenames enclosed in single quotes
        with the temporary chart path.
        """
        # Use the existing cleaner instance and configure the context (if needed)
        handler = self.cleaner
        handler.context = MagicMock()
        # Provide a code string with a png filename enclosed in single quotes.
        code = "Image path: 'mychart.png'"
        # Build the expected replacement string using the DEFAULT_CHART_DIRECTORY.
        expected_path = str(Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png")
        expected_code = f"Image path: '{expected_path}'"
        # Call the function to replace the filename.
        result = handler._replace_output_filenames_with_temp_chart(code)
        # Assert that the replacement is done correctly.
        self.assertEqual(result, expected_code)

    def test_get_target_names_single_name(self):
        """
        Test get_target_names with a single ast.Name target to ensure it returns the correct target name,
        that the is_slice flag is False (since there is no subscript), and that the returned target is the same.
        """
        single_node = ast.Name(id="single", ctx=ast.Store())
        target_names, is_slice, last_target = self.cleaner.get_target_names(
            [single_node]
        )
        self.assertEqual(target_names, ["single"])
        self.assertFalse(is_slice)
        self.assertEqual(last_target, single_node)

    def test_validate_and_make_table_name_case_sensitive_sql_query(self):
        """
        Test that _validate_and_make_table_name_case_sensitive properly cleans a SQL query
        assigned to the variable 'sql_query' by removing the trailing semicolon.
        """
        table = self.sample_df.schema.name
        # Create an AST assignment node with target "sql_query"
        node = ast.Assign(
            targets=[ast.Name(id="sql_query", ctx=ast.Store())],
            value=ast.Constant(value=f"SELECT * FROM {table};"),
        )
        self.cleaner.context.dfs = [self.sample_df]
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        # The trailing semicolon should be removed from the SQL query.
        self.assertEqual(updated_node.value.value, f"SELECT * FROM {table}")

    def test_validate_and_make_table_name_case_sensitive_non_sql_assign(self):
        """
        Test that _validate_and_make_table_name_case_sensitive leaves an AST.Assign node unchanged
        when the target variable is not "sql_query" or "query". This ensures that nodes not containing
        an SQL query string are not modified.
        """
        # Create an AST Assign node with a target name that is not 'sql_query' or 'query'.
        # The value is a string that looks like SQL but should not be cleaned because the target name doesn't match.
        original_query = "This is not an SQL query;"
        node = ast.Assign(
            targets=[ast.Name(id="random_var", ctx=ast.Store())],
            value=ast.Constant(value=original_query),
        )
        # Save the original source code for comparison.
        original_node_source = astor.to_source(node)
        # Call the method to validate and possibly clean the node.
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        # Assert that the node remains unchanged.
        self.assertEqual(astor.to_source(updated_node), original_node_source)

    def test_validate_and_make_table_name_case_sensitive_assign_call(self):
        """
        Test that _validate_and_make_table_name_case_sensitive cleans SQL queries in assignment nodes
        where the value is a call to execute_sql_query by removing trailing semicolons.
        """
        table = self.sample_df.schema.name
        # Ensure the context has the sample dataframe for allowed table names.
        self.cleaner.context.dfs = [self.sample_df]
        # Create an assignment node where the value is a call to execute_sql_query with a SQL query.
        node = ast.Assign(
            targets=[ast.Name(id="dummy", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
                args=[ast.Constant(value=f"SELECT * FROM {table};")],
                keywords=[],
            ),
        )
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        # Verify that the SQL query no longer has a trailing semicolon.
        self.assertEqual(updated_node.value.args[0].value, f"SELECT * FROM {table}")

    def test_validate_and_make_table_name_case_sensitive_non_constant_value(self):
        """
        Test that _validate_and_make_table_name_case_sensitive leaves an AST.Assign node unchanged
        when its value is not a Constant (even if the target variable name is 'sql_query'). This ensures
        that only constant SQL query strings are modified.
        """
        table = self.sample_df.schema.name
        # Create a node where the SQL query is constructed via a binary operation instead of a Constant.
        node = ast.Assign(
            targets=[ast.Name(id="sql_query", ctx=ast.Store())],
            value=ast.BinOp(
                left=ast.Constant(value="SELECT * FROM "),
                op=ast.Add(),
                right=ast.Constant(value=table),
            ),
        )
        original_source = astor.to_source(node)
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        # Since the SQL query expression is not a Constant, it should remain unmodified.
        self.assertEqual(astor.to_source(updated_node), original_source)

    def test_get_target_names_with_invalid_and_valid(self):
        """
        Test get_target_names with a mix of an invalid target (which should be ignored)
        and a valid target, ensuring that only the valid target's name is collected and
        returned as the last target.
        """
        # Create an invalid target (ast.Call) and a valid target (ast.Name)
        invalid_target = ast.Call(
            func=ast.Name(id="foo", ctx=ast.Load()), args=[], keywords=[]
        )
        valid_target = ast.Name(id="valid", ctx=ast.Store())
        # Pass the targets in order: first invalid then valid.
        targets = [invalid_target, valid_target]
        names, is_slice, last_target = self.cleaner.get_target_names(targets)
        self.assertEqual(
            names, ["valid"], "Expected only the valid target's name to be collected."
        )
        self.assertFalse(
            is_slice, "Expected the is_slice flag to be False for an ast.Name target."
        )
        self.assertEqual(
            last_target,
            valid_target,
            "Expected the last_target to be the valid target.",
        )

    def test_clean_code_invalid_python(self):
        """
        Test that clean_code() raises a SyntaxError when provided with invalid Python code.
        This ensures that the cleaning process fails fast if the code cannot be parsed.
        ... existing code
        """
        # Provide an invalid Python code string that will cause a SyntaxError in ast.parse.
        invalid_code = "def bad_code(:\n    pass"
        with self.assertRaises(SyntaxError):
            self.cleaner.clean_code(invalid_code)
