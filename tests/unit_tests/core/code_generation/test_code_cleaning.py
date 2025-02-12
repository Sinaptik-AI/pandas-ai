import ast
import os
import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock
import pandas as pd
from pandasai.agent.state import AgentState
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError
from unittest.mock import patch
from pandasai.core.code_execution.code_executor import CodeExecutor

class FakeDataFrame:
    """
    A fake DataFrame object to simulate the minimal attributes needed for testing.
    """
    def __init__(self, name):
        # Create a fake schema with a 'name' attribute.
        self.schema = type("FakeSchema", (), {"name": name})
        # Simulate dummy columns (used in get_head for comparison).
        self.columns = pd.Index(["col1", "col2"])
    def get_head(self):
        # Return a simple Pandas DataFrame with preset columns.
        return pd.DataFrame(columns=self.columns)
class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # Setup a mock context for CodeCleaner with a proper DataFrame.
        self.context = MagicMock(spec=AgentState)
        self.cleaner = CodeCleaner(self.context)
        self.sample_df = DataFrame({
            "country": ["United States", "United Kingdom", "Japan", "China"],
            "gdp": [
                19294482071552,
                2891615567872,
                4380756541440,
                14631844184064,
            ],
            "happiness_index": [6.94, 7.22, 5.87, 5.12],
        })
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
        result = self.cleaner._replace_table_names(sql_query, table_names, allowed_table_names)
        self.assertEqual(result, "SELECT * FROM my_table;")
    def test_replace_table_names_invalid(self):
        sql_query = "SELECT * FROM my_table;"
        table_names = ["my_table"]
        allowed_table_names = {}
        with self.assertRaises(MaliciousQueryError):
            self.cleaner._replace_table_names(sql_query, table_names, allowed_table_names)
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
        updated_node = self.cleaner.extract_fix_dataframe_redeclarations(node, code_lines)
        self.assertIsInstance(updated_node, ast.AST)
    def test_replace_output_filenames_with_temp_chart(self):
        handler = self.cleaner
        handler.context = MagicMock()
        handler.context.config.save_charts = True
        handler.context.logger = MagicMock()  # Mock logger
        handler.context.last_prompt_id = 123
        handler.context.config.save_charts_path = "/custom/path"
        code = 'some text "hello.png" more text'
        result = handler._replace_output_filenames_with_temp_chart(code)
        expected_code = f'some text "{os.path.join("exports", "charts", "temp_chart.png")}" more text'
        self.assertEqual(result, expected_code)
    def test_replace_output_filenames_with_temp_chart_empty_code(self):
        handler = self.cleaner
        code = ""
        expected_code = ""  # It should remain empty, as no substitution is made
        result = handler._replace_output_filenames_with_temp_chart(code)
        self.assertEqual(result, expected_code, f"Expected '{expected_code}', but got '{result}'")
    def test_replace_output_filenames_with_temp_chart_no_png(self):
        handler = self.cleaner
        code = "some text without png"
        expected_code = "some text without png"  # No change should occur
        result = handler._replace_output_filenames_with_temp_chart(code)
        self.assertEqual(result, expected_code, f"Expected '{expected_code}', but got '{result}'")
    def test_clean_code_multiline(self):
        """
        Verify that clean_code processes various code elements correctly:
        - Removes the direct SQL execution function definition.
        - Cleans SQL queries by stripping trailing semicolons.
        - Removes plt.show() calls.
        - Replaces .png filenames in strings with the temporary chart path.
        """
        table = self.sample_df.schema.name
        code = f'''def execute_sql_query(query):
    pass
query = "SELECT * FROM {table};"
plt.show()
print("Chart image: 'chart.png'")
'''
        self.cleaner.context.dfs = [self.sample_df]
        cleaned_code = self.cleaner.clean_code(code)
        # Verify that the direct SQL execution function definition is removed.
        self.assertNotIn("def execute_sql_query", cleaned_code)
        # Verify that the plt.show() call is removed.
        self.assertNotIn("plt.show()", cleaned_code)
        # Verify that the SQL query does not end with a semicolon.
        self.assertIn(f"SELECT * FROM {table}", cleaned_code)
        self.assertNotIn(f"SELECT * FROM {table};", cleaned_code)
        # Verify that any .png file reference is replaced with the temporary chart filename.
        self.assertIn("temp_chart.png", cleaned_code)
    def test_clean_code_multiline_with_fake_dataframe(self):
        """
        Verify that clean_code works correctly when using a FakeDataFrame object.
        """
        # Use a fake DataFrame with a defined schema name.
        fake_df = FakeDataFrame("my_table")
        table = fake_df.schema.name
        code = f'''def execute_sql_query(query):
    pass
query = "SELECT * FROM {table};"
plt.show()
print("Chart image: 'chart.png'")
'''
        self.cleaner.context.dfs = [fake_df]
        cleaned_code = self.cleaner.clean_code(code)
        self.assertNotIn("def execute_sql_query", cleaned_code)
        self.assertNotIn("plt.show()", cleaned_code)
        self.assertIn(f"SELECT * FROM {table}", cleaned_code)
        self.assertNotIn(f"SELECT * FROM {table};", cleaned_code)
        self.assertIn("temp_chart.png", cleaned_code)
if __name__ == "__main__":
    unittest.main()
    def test_validate_and_make_table_name_case_sensitive_sql_call(self):
        """
        Test that _validate_and_make_table_name_case_sensitive correctly cleans SQL queries
        when provided as a call to execute_sql_query in both Assign and Expr nodes.
        """
        table = self.sample_df.schema.name
        # Set the dfs in context so that table names become allowed.
        self.cleaner.context.dfs = [self.sample_df]
        # Create an Assign node with a call to execute_sql_query
        call_node_assign = ast.Call(
            func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
            args=[ast.Constant(value=f"SELECT * FROM {table};")],
            keywords=[],
        )
        assign_node = ast.Assign(
            targets=[ast.Name(id="sql_query", ctx=ast.Store())],
            value=call_node_assign,
        )
        # Process the Assign node
        updated_assign = self.cleaner._validate_and_make_table_name_case_sensitive(assign_node)
        # The query should have its trailing semicolon removed.
        self.assertEqual(updated_assign.value.args[0].value, f"SELECT * FROM {table}")
        # Create an Expr node with a call to execute_sql_query
        call_node_expr = ast.Call(
            func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
            args=[ast.Constant(value=f"SELECT * FROM {table};")],
            keywords=[],
        )
        expr_node = ast.Expr(value=call_node_expr)
        # Process the Expr node
        updated_expr = self.cleaner._validate_and_make_table_name_case_sensitive(expr_node)
        self.assertEqual(updated_expr.value.args[0].value, f"SELECT * FROM {table}")
    def test_extract_fix_dataframe_redeclarations_non_df(self):
        """
        Test that extract_fix_dataframe_redeclarations returns None for assignments that
        are not DataFrame redeclarations.
        """
        # Create an assignment node that is not a pd.DataFrame declaration.
        node = ast.Assign(
            targets=[ast.Name(id="x", ctx=ast.Store())],
            value=ast.Constant(value=42)
        )
        code_lines = ["x = 42"]  # A minimal code snippet that does not declare any DataFrame
        
        result = self.cleaner.extract_fix_dataframe_redeclarations(node, code_lines)
        self.assertIsNone(result)
    def test_extract_fix_dataframe_redeclarations_with_slice(self):
        """
        Test extract_fix_dataframe_redeclarations with a subscript target (e.g., df[0]).
        The test patches CodeExecutor.execute to return a dictionary with "df" as a list
        containing the sample_df and verifies that the returned assignment references
        the corresponding dataframe from dfs.
        """
        # Create an assignment node using a subscript (df[0])
        assign_node = ast.Assign(
            targets=[ast.Subscript(
                value=ast.Name(id="df", ctx=ast.Store()),
                slice=ast.Index(value=ast.Constant(value=0)),
                ctx=ast.Store(),
            )],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="DataFrame",
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            ),
        )
        code_lines = [
            "df[0] = pd.DataFrame({})"
        ]
        # Set up the context with a valid dataframe
        self.cleaner.context.dfs = [self.sample_df]
        # Patch CodeExecutor.execute to return {"df": [self.sample_df]}
        with patch("pandasai.core.code_generation.code_cleaning.CodeExecutor.execute", return_value={"df": [self.sample_df]}):
            updated_node = self.cleaner.extract_fix_dataframe_redeclarations(assign_node, code_lines)
        # Verify that an updated assignment node is returned
        self.assertIsNotNone(updated_node)
        self.assertIsInstance(updated_node, ast.Assign)
        # Verify that the target is a Subscript with id "df"
        target = updated_node.targets[0]
        self.assertTrue(isinstance(target, ast.Subscript))
        self.assertEqual(target.value.id, "df")
        # Verify that the replacement value references "dfs" instead of "df"
        self.assertTrue(isinstance(updated_node.value, ast.Subscript))
        self.assertEqual(updated_node.value.value.id, "dfs")
        # Check that the index in the subscript (the slice) is 0
        # Depending on Python version, ast.Index might wrap the constant/number
        slice_obj = updated_node.value.slice
        if hasattr(slice_obj, "value"):
            self.assertEqual(slice_obj.value.value, 0)
        else:
            self.assertEqual(slice_obj.n, 0)import ast
import pandas as pd
from pandasai.core.code_generation.code_cleaning import CodeCleaner


def test_get_target_names_and_check_is_df_declaration(self):
    """
    Test that get_target_names correctly extracts target names (including Subscript targets)
    and that check_is_df_declaration correctly identifies DataFrame declarations.
    """
    # Create two targets: one ast.Name and one ast.Subscript.
    name_target = ast.Name(id="df1", ctx=ast.Store())
    subscript_target = ast.Subscript(
        value=ast.Name(id="df2", ctx=ast.Load()),
        slice=ast.Index(ast.Constant(value=0)),
        ctx=ast.Store()
    )
    targets = [name_target, subscript_target]
    
    # Test get_target_names, it should return both target names with is_slice True since the last target is a Subscript.
    target_names, is_slice, last_target = self.cleaner.get_target_names(targets)
    self.assertEqual(target_names, ["df1", "df2"])
    self.assertTrue(is_slice)  # Expect True because a subscript target is present.

    # Test check_is_df_declaration with a valid pd.DataFrame call.
    pd_dataframe_call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="pd", ctx=ast.Load()),
            attr="DataFrame",
            ctx=ast.Load()
        ),
        args=[],
        keywords=[]
    )
    assign_node = ast.Assign(
        targets=[name_target],
        value=pd_dataframe_call
    )
    self.assertTrue(self.cleaner.check_is_df_declaration(assign_node))

    # Test check_is_df_declaration with a node that is not a DataFrame declaration.
    non_df_call = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="pd", ctx=ast.Load()),
            attr="something_else",
            ctx=ast.Load()
        ),
        args=[],
        keywords=[]
    )
    assign_node2 = ast.Assign(
        targets=[name_target],
        value=non_df_call
    )
    self.assertFalse(self.cleaner.check_is_df_declaration(assign_node2))
# ... existing code in TestCodeCleaner continues
import ast
import re
import unittest
import pandas as pd
from types import SimpleNamespace
from unittest.mock import patch

from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.core.code_execution.code_executor import CodeExecutor


class DummyDF:
    """
    A dummy dataframe wrapper that mimics the necessary properties for the tests.
    """
    def __init__(self, name, df):
        # Create a dummy schema object with attribute `name`
        self.schema = type("Schema", (), {"name": name})
        self._df = df

    def get_head(self):
        return self._df


class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        """
        Set up a dummy context with a configuration and a dfs list for each test.
        """
        # Create a simple pandas DataFrame (using a very simple df)
        self.pd_df = pd.DataFrame({"col": [1]})
        self.dummy_df = DummyDF("table1", self.pd_df)
        self.context = SimpleNamespace(dfs=[self.dummy_df], config={})
        self.cleaner = CodeCleaner(self.context)

    def test_get_target_names_and_check_is_df_declaration(self):
        """
        Test that get_target_names correctly extracts target names (including Subscript targets)
        and that check_is_df_declaration correctly identifies DataFrame declarations.
        """
        # Create two targets: one ast.Name and one ast.Subscript.
        name_target = ast.Name(id="df1", ctx=ast.Store())
        subscript_target = ast.Subscript(
            value=ast.Name(id="df2", ctx=ast.Load()),
            slice=ast.Index(ast.Constant(value=0)),
            ctx=ast.Store()
        )
        targets = [name_target, subscript_target]

        # Test get_target_names: it should return both target names, and is_slice True because the last target is a Subscript.
        target_names, is_slice, last_target = self.cleaner.get_target_names(targets)
        self.assertEqual(target_names, ["df1", "df2"])
        self.assertTrue(is_slice)  # Expect True since a subscript target is present.

        # Test check_is_df_declaration with a valid pd.DataFrame call.
        pd_dataframe_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="DataFrame",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node = ast.Assign(
            targets=[name_target],
            value=pd_dataframe_call
        )
        self.assertTrue(self.cleaner.check_is_df_declaration(assign_node))

        # Test check_is_df_declaration with a node that is not a DataFrame declaration.
        non_df_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="something_else",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node2 = ast.Assign(
            targets=[name_target],
            value=non_df_call
        )
        self.assertFalse(self.cleaner.check_is_df_declaration(assign_node2))

    def test_validate_and_make_table_name_case_sensitive_sql_call(self):
        """
        Test that _validate_and_make_table_name_case_sensitive correctly cleans SQL query strings
        and that direct SQL function-call nodes are updated appropriately.
        """
        # Prepare a node representing a direct SQL query call using execute_sql_query.
        sql_query = "SELECT * FROM table1;"
        call_node = ast.Call(
            func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
            args=[ast.Constant(value=sql_query)],
            keywords=[]
        )
        expr_node = ast.Expr(value=call_node)

        # Set the context dfs so that allowed table names are available.
        # self.context.dfs was set up in setUp to include dummy_df with schema.name "table1".

        # Call the _validate_and_make_table_name_case_sensitive method to modify the node.
        new_node = self.cleaner._validate_and_make_table_name_case_sensitive(expr_node)

        # The cleaned query should have the trailing semicolon removed.
        cleaned_query = new_node.value.args[0].value
        self.assertEqual(cleaned_query, "SELECT * FROM table1")

    def test_extract_fix_dataframe_redeclarations_with_slice(self):
        """
        Test that a dataframe redeclaration with a subscript target is properly fixed by replacing 
        the declaration with a reference to the corresponding dataframe in `dfs`.
        """
        # Create an AST assign node for a dataframe declaration with a subscript target.
        subscript_target = ast.Subscript(
            value=ast.Name(id="df2", ctx=ast.Load()),
            slice=ast.Index(ast.Constant(value=0)),
            ctx=ast.Store()
        )
        # Construct a call node for pd.DataFrame (i.e., pd.DataFrame({...}))
        dataframe_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="DataFrame",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node = ast.Assign(
            targets=[subscript_target],
            value=dataframe_call
        )
        # This is our code lines corresponding to the code. They should build the same assignment.
        code_lines = [
            "import pandas as pd",
            "df2 = [pd.DataFrame({'col':[1]})]"
        ]

        # We need to force CodeExecutor.execute to return an environment such that:
        # env["df2"][0] equals the dataframe we want to match.
        # We use our previously created self.pd_df for that match.
        dummy_env = {"df2": [self.pd_df]}

        # Patch the execute method of CodeExecutor to always return our dummy environment.
        original_execute = CodeExecutor.execute
        try:
            CodeExecutor.execute = lambda self, code: dummy_env  # override for this test
            new_node = self.cleaner.extract_fix_dataframe_redeclarations(assign_node, code_lines)
        finally:
            CodeExecutor.execute = original_execute

        # Check that an AST.Assign node is returned (and not None).
        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, ast.Assign)

        # The target should now be a subscript referencing 'df2' (or the original target variable)
        # and the new value should be a subscript accessing the dummy dfs list at index 0.
        self.assertEqual(len(new_node.targets), 1)
        new_target = new_node.targets[0]
        self.assertTrue(isinstance(new_target, ast.Subscript))
        # Check that the subscript of the new target has the same slice as in the original node.
        # Due to AST differences in Python versions, we allow either ast.Constant or ast.Num.
        original_slice = subscript_target.slice
        new_slice = new_target.slice
        if isinstance(new_slice, ast.Index):
            # Check the index value inside the Index. It can be an ast.Constant or ast.Num.
            if hasattr(new_slice.value, "n"):
                slice_value = new_slice.value.n
            elif hasattr(new_slice.value, "value"):
                slice_value = new_slice.value.value
            else:
                slice_value = None
            if hasattr(original_slice, "value"):
                if hasattr(original_slice.value, "n"):
                    original_slice_value = original_slice.value.n
                else:
                    original_slice_value = original_slice.value.value
            else:
                original_slice_value = None
            self.assertEqual(slice_value, original_slice_value)

        # Also verify that the new value of the assignment is a Subscript accessing 'dfs' at index 0.
        new_value = new_node.value
        self.assertIsInstance(new_value, ast.Subscript)
        self.assertIsInstance(new_value.value, ast.Name)
        self.assertEqual(new_value.value.id, "dfs")
        # Again check the slice value to be 0.
        if isinstance(new_value.slice, ast.Index):
            if hasattr(new_value.slice.value, "n"):
                index_value = new_value.slice.value.n
            elif hasattr(new_value.slice.value, "value"):
                index_value = new_value.slice.value.value
            else:
                index_value = None
            self.assertEqual(index_value, 0)
        else:
            # In Python 3.9+, the slice attribute might directly be an ast.Constant.
            if hasattr(new_value.slice, "value"):
                self.assertEqual(new_value.slice.value, 0)
            else:
                self.fail("Unexpected AST structure for slice.")

# ... existing code if any

if __name__ == "__main__":
    unittest.main()
import ast
import re
import unittest
import pandas as pd
from types import SimpleNamespace
from unittest.mock import patch

from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.core.code_execution.code_executor import CodeExecutor


class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        """
        Set up a dummy context with a configuration and a dfs list for each test.
        """
        # Create a simple pandas DataFrame (using a very simple df)
        self.pd_df = pd.DataFrame({"col": [1]})
        # DummyDF mimics necessary df attributes and behaviors.
        class DummyDF:
            def __init__(self, name, df):
                self.schema = type("Schema", (), {"name": name})
                self._df = df
            def get_head(self):
                return self._df
        self.dummy_df = DummyDF("table1", self.pd_df)
        self.context = SimpleNamespace(dfs=[self.dummy_df], config={})
        self.cleaner = CodeCleaner(self.context)

    def test_get_target_names_and_check_is_df_declaration(self):
        """
        Test that get_target_names correctly extracts target names (including Subscript targets)
        and that check_is_df_declaration correctly identifies DataFrame declarations.
        """
        # Create two targets: one ast.Name and one ast.Subscript.
        name_target = ast.Name(id="df1", ctx=ast.Store())
        subscript_target = ast.Subscript(
            value=ast.Name(id="df2", ctx=ast.Load()),
            slice=ast.Index(ast.Constant(value=0)) if hasattr(ast, "Index") else ast.Constant(value=0),
            ctx=ast.Store()
        )
        targets = [name_target, subscript_target]

        # Test get_target_names: it should return both target names, and is_slice True because the last target is a Subscript.
        target_names, is_slice, last_target = self.cleaner.get_target_names(targets)
        self.assertEqual(target_names, ["df1", "df2"])
        self.assertTrue(is_slice)  # Expect True since a subscript target is present.

        # Test check_is_df_declaration with a valid pd.DataFrame call.
        pd_dataframe_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="DataFrame",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node = ast.Assign(
            targets=[name_target],
            value=pd_dataframe_call
        )
        self.assertTrue(self.cleaner.check_is_df_declaration(assign_node))

        # Test check_is_df_declaration with a node that is not a DataFrame declaration.
        non_df_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="something_else",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node2 = ast.Assign(
            targets=[name_target],
            value=non_df_call
        )
        self.assertFalse(self.cleaner.check_is_df_declaration(assign_node2))

    def test_validate_and_make_table_name_case_sensitive_sql_call(self):
        """
        Test that _validate_and_make_table_name_case_sensitive correctly cleans SQL query strings
        and that direct SQL function-call nodes are updated appropriately.
        """
        # Prepare a node representing a direct SQL query call using execute_sql_query.
        sql_query = "SELECT * FROM table1;"
        call_node = ast.Call(
            func=ast.Name(id="execute_sql_query", ctx=ast.Load()),
            args=[ast.Constant(value=sql_query)],
            keywords=[]
        )
        expr_node = ast.Expr(value=call_node)

        # Call the _validate_and_make_table_name_case_sensitive method to modify the node.
        new_node = self.cleaner._validate_and_make_table_name_case_sensitive(expr_node)

        # The cleaned query should have the trailing semicolon removed.
        cleaned_query = new_node.value.args[0].value
        self.assertEqual(cleaned_query, "SELECT * FROM table1")

    def test_extract_fix_dataframe_redeclarations_with_slice_new_ast(self):
        """
        Test that a dataframe redeclaration with a subscript target is properly fixed by replacing 
        the declaration with a reference to the corresponding dataframe in `dfs`, accommodating for 
        differences in AST slice representations across Python versions.
        """
        # Create an AST assign node for a dataframe declaration with a subscript target.
        subscript_target = ast.Subscript(
            value=ast.Name(id="df2", ctx=ast.Load()),
            slice=ast.Index(ast.Constant(value=0)) if hasattr(ast, "Index") else ast.Constant(value=0),
            ctx=ast.Store()
        )
        # Construct a call node for pd.DataFrame (i.e., pd.DataFrame({...}))
        dataframe_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="DataFrame",
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
        assign_node = ast.Assign(
            targets=[subscript_target],
            value=dataframe_call
        )
        # These code lines should correspond to the assignment.
        code_lines = [
            "import pandas as pd",
            "df2 = [pd.DataFrame({'col':[1]})]"
        ]

        # Prepare a dummy environment so that env["df2"][0] equals the expected dataframe.
        dummy_env = {"df2": [self.pd_df]}

        # Patch CodeExecutor.execute to return the dummy environment.
        original_execute = CodeExecutor.execute
        try:
            CodeExecutor.execute = lambda self, code: dummy_env
            new_node = self.cleaner.extract_fix_dataframe_redeclarations(assign_node, code_lines)
        finally:
            CodeExecutor.execute = original_execute

        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, ast.Assign)
        self.assertEqual(len(new_node.targets), 1)
        new_target = new_node.targets[0]

        # Helper to extract the slice value regardless of AST differences.
        def get_slice_val(slice_node):
            # For Python versions before 3.9, slice may be wrapped in ast.Index.
            if isinstance(slice_node, ast.Index):
                s = slice_node.value
            else:
                s = slice_node
            if hasattr(s, "n"):
                return s.n
            elif hasattr(s, "value"):
                return s.value
            return None

        # Verify that the subscript target slice evaluates to 0.
        self.assertEqual(get_slice_val(new_target.slice), 0)
        new_value = new_node.value
        self.assertIsInstance(new_value, ast.Subscript)
        self.assertIsInstance(new_value.value, ast.Name)
        self.assertEqual(new_value.value.id, "dfs")
        # Also confirm that the index accessed from the new value is 0.
        self.assertEqual(get_slice_val(new_value.slice), 0)

# ... existing code if any

if __name__ == "__main__":
    unittest.main()
