import ast
import os
import unittest
from unittest.mock import MagicMock
from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pathlib import Path

# No additional imports are needed beyond what is already present in the test file.
# No additional imports are needed beyond what is already present in the tests file.
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
    def test_validate_expr_node_execute_sql_query(self):
        """
        Test that an ast.Expr node with a call to execute_sql_query is properly cleaned,
        ensuring that a trailing semicolon is trimmed from the SQL query.
        """
        table = self.sample_df.schema.name
        # Create an ast.Expr node representing a call to execute_sql_query with a SQL query value ending with a semicolon.
        node = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
                args=[ast.Constant(value=f"SELECT * FROM {table};")],
                keywords=[],
            )
        )
        # Set the context to contain our sample_df so that the allowed table names are set correctly.
        self.cleaner.context.dfs = [self.sample_df]
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        # The SQL query should have its trailing semicolon removed.
        self.assertEqual(updated_node.value.args[0].value, f"SELECT * FROM {table}")
    def test_clean_code_full_flow(self):
        """
        Test that clean_code processes multiple nodes correctly:
            - It removes a direct SQL execution function definition.
            - It cleans SQL queries by removing trailing semicolons.
            - It removes plt.show() calls.
            - It replaces .png filenames with the temporary chart path.
        """
        # Set up the context with the sample DataFrame so that table names are allowed.
        self.cleaner.context.dfs = [self.sample_df]
        table = self.sample_df.schema.name
        # Prepare a multi-line code string containing:
        # - A function definition for "execute_sql_query" (which should be skipped).
        # - An assignment with a SQL query ending with a semicolon.
        # - A plt.show() call which should be removed.
        # - A print statement referencing a png file which should be replaced.
        code = f'''
def execute_sql_query(query):
    pass
query = "SELECT * FROM {table};"
plt.show()
print("This is a chart: 'chart.png'")
        '''
        cleaned = self.cleaner.clean_code(code)
        # Ensure the function definition for execute_sql_query is removed.
        self.assertNotIn("def execute_sql_query", cleaned)
        # Ensure that there is no plt.show() call present.
        self.assertNotIn("plt.show", cleaned)
        # Ensure the SQL query does not include a trailing semicolon.
        self.assertIn(f"SELECT * FROM {table}", cleaned)
        self.assertNotIn(f"SELECT * FROM {table};", cleaned)
        # Check that the .png file is replaced with temp_chart.png using the DEFAULT_CHART_DIRECTORY.
        chart_path = Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png"
        expected_png = str(chart_path)
        self.assertIn(expected_png, cleaned)
        self.assertNotIn("chart.png", cleaned)
    def test_get_target_names_with_subscript(self):
        """
        Test that get_target_names correctly extracts the target name from an ast.Subscript,
        sets the is_slice flag to True, and returns the proper target object.
        """
        # Construct an ast.Subscript target: e.g., df[0]
        target_node = ast.Subscript(
            value=ast.Name(id="df", ctx=ast.Load()),
            slice=ast.Index(value=ast.Num(n=0)),
            ctx=ast.Store(),
        )
        # Call get_target_names with a list containing our subscript node.
        target_names, is_slice, returned_target = self.cleaner.get_target_names([target_node])
        # Verify that the target name list contains "df".
        self.assertEqual(target_names, ["df"])
        # Verify that the is_slice flag is True.
        self.assertTrue(is_slice)
        # Verify that the returned target is the same as the passed target_node.
        self.assertEqual(returned_target, target_node)
    def test_replace_table_names_multiple_valid(self):
        """
        Test that _replace_table_names correctly replaces multiple occurrences of table names 
        in a query with authorized and case-sensitive names.
        """
        # Prepare a query with two table names used multiple times.
        sql_query = "SELECT * FROM table_one JOIN table_two ON table_one.id = table_two.id;"
        table_names = ["table_one", "table_two"]
        allowed_table_names = {
            "table_one": '"table_one"',
            "table_two": '"table_two"'
        }
        result = self.cleaner._replace_table_names(sql_query, table_names, allowed_table_names)
        expected_query = 'SELECT * FROM "table_one" JOIN "table_two" ON "table_one".id = "table_two".id;'
        self.assertEqual(result, expected_query)import ast


    def test_check_is_df_declaration(self):
        """
        Test that check_is_df_declaration returns True for a valid DataFrame declaration
        (i.e., a pd.DataFrame call) and returns False for an invalid one (e.g., a pd.Series call).
        """
        # ... existing code

        # Construct a valid DataFrame declaration node: df = pd.DataFrame({...})
        valid_node = ast.Assign(
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
            self.cleaner.check_is_df_declaration(valid_node),
            "Expected valid pd.DataFrame declaration to return True",
        )

        # Construct an invalid DataFrame declaration node: df = pd.Series([...])
        invalid_node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="Series",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.assertFalse(
            self.cleaner.check_is_df_declaration(invalid_node),
            "Expected pd.Series declaration to return False",
        )
import ast
import unittest
from pathlib import Path
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.agent.state import AgentState


class DummyState(AgentState):
    def __init__(self):
        # Provide dummy values for attributes used in CodeCleaner
        self.config = {}
        self.dfs = []

class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # ... existing code for setting up CodeCleaner
        self.context = DummyState()
        self.cleaner = CodeCleaner(self.context)

    def test_check_is_df_declaration(self):
        """
        Test that check_is_df_declaration returns True for a valid DataFrame declaration
        (i.e., a pd.DataFrame call) and returns False for an invalid one (e.g., a pd.Series call).
        """
        # Construct a valid DataFrame declaration node: df = pd.DataFrame({...})
        valid_node = ast.Assign(
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
            self.cleaner.check_is_df_declaration(valid_node),
            "Expected valid pd.DataFrame declaration to return True",
        )

        # Construct an invalid DataFrame declaration node: df = pd.Series([...])
        invalid_node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="Series",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.assertFalse(
            self.cleaner.check_is_df_declaration(invalid_node),
            "Expected pd.Series declaration to return False",
        )

    def test_replace_output_filenames_with_temp_chart(self):
        """
        Test that the clean_code method correctly replaces any .png filename with
        the temporary chart path constructed from DEFAULT_CHART_DIRECTORY and "temp_chart.png".
        """
        # Prepare code that includes a .png filename
        original_png = "my_image.png"
        code = f'print("Logging image: \'{original_png}\'")'

        # Call clean_code to perform file name replacement
        cleaned_code = self.cleaner.clean_code(code)

        # Construct the expected temporary chart path as a string.
        expected_chart_path = str(Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png")

        # Assert that the expected temporary chart path is found in the cleaned code.
        self.assertIn(
            expected_chart_path,
            cleaned_code,
            "Temporary chart path not found in cleaned code.",
        )
        # Also assert that the original png name is no longer present.
        self.assertNotIn(
            original_png,
            cleaned_code,
            "Original png filename should be replaced in cleaned code.",
        )

# ... existing code if needed for running tests
if __name__ == "__main__":
    unittest.main()
import ast
import unittest
from pathlib import Path
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.agent.state import AgentState


class DummyState(AgentState):
    def __init__(self):
        # Provide dummy values for attributes used in CodeCleaner
        self.config = {}
        self.dfs = []

class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # ... existing code for setting up CodeCleaner
        self.context = DummyState()
        self.cleaner = CodeCleaner(self.context)

    def test_check_is_df_declaration(self):
        """
        Test that check_is_df_declaration returns True for a valid DataFrame declaration
        (i.e., a pd.DataFrame call) and returns False for an invalid one (e.g., a pd.Series call).
        """
        # Construct a valid DataFrame declaration node: df = pd.DataFrame({...})
        valid_node = ast.Assign(
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
            self.cleaner.check_is_df_declaration(valid_node),
            "Expected valid pd.DataFrame declaration to return True",
        )

        # Construct an invalid DataFrame declaration node: df = pd.Series([...])
        invalid_node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="Series",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.assertFalse(
            self.cleaner.check_is_df_declaration(invalid_node),
            "Expected pd.Series declaration to return False",
        )

    def test_replace_output_filenames_with_temp_chart(self):
        """
        Test that the clean_code method correctly replaces any .png filename with
        the temporary chart path constructed from DEFAULT_CHART_DIRECTORY and "temp_chart.png".
        """
        # Prepare code that includes a .png filename
        original_png = "my_image.png"
        code = f'print("Logging image: \'{original_png}\'")'

        # Call clean_code to perform file name replacement
        cleaned_code = self.cleaner.clean_code(code)

        # Construct the expected temporary chart path as a string.
        expected_chart_path = str(Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png")

        # Assert that the expected temporary chart path is found in the cleaned code.
        self.assertIn(
            expected_chart_path,
            cleaned_code,
            "Temporary chart path not found in cleaned code.",
        )
        # Assert that the original PNG filename is no longer present.
        self.assertNotIn(
            original_png,
            cleaned_code,
            "Original PNG filename should be replaced in cleaned code.",
        )

    def test_clean_code_replaces_png_filename(self):
        """
        Test that clean_code replaces the original PNG filename with the temporary chart path.
        This test ensures that the expected temporary chart path appears in the cleaned code
        and the original PNG filename is removed.
        """
        original_png = "my_image.png"
        code = f'print("Logging image: \'{original_png}\'")'
        cleaned_code = self.cleaner.clean_code(code)
        expected_chart_path = str(Path(DEFAULT_CHART_DIRECTORY) / "temp_chart.png")
        self.assertIn(
            expected_chart_path,
            cleaned_code,
            "Temporary chart path not found in cleaned code.",
        )
        self.assertNotIn(
            original_png,
            cleaned_code,
            "Original PNG filename should be replaced in cleaned code.",
        )

    # ... existing code if needed for additional tests

if __name__ == "__main__":
    unittest.main()
