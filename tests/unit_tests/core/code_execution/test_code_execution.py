import unittest
from unittest.mock import MagicMock
import ast
from pandasai.core.code_execution.code_executor import CodeExecutor
from pandasai.config import Config
from pandasai.exceptions import NoResultFoundError


class TestCodeExecutor(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock(specs=Config)
        self.executor = CodeExecutor(self.config)

    def test_initialization(self):
        """Test initialization of CodeExecutor."""
        self.assertIsInstance(self.executor._environment, dict)
        self.assertEqual(self.executor._plots, [])

    def test_add_to_env(self):
        """Test adding a variable to the environment."""
        self.executor.add_to_env("test_var", 42)
        self.assertEqual(self.executor._environment["test_var"], 42)

    def test_execute_valid_code(self):
        """Test executing valid code."""
        code = "result = 5 + 5"
        self.executor.execute(code)
        self.assertEqual(self.executor._environment["result"], 10)

    def test_execute_code_with_variable(self):
        """Test executing code that defines a variable."""
        code = "my_list = [1, 2, 3]"
        self.executor.execute(code)
        self.assertEqual(self.executor._environment["my_list"], [1, 2, 3])

    def test_execute_and_return_result(self):
        """Test executing code and returning the result."""
        code = "result = 3 * 3"
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, 9)

    def test_execute_and_return_result_no_result(self):
        """Test execution when no result is returned."""
        code = "x = 10"
        with self.assertRaises(NoResultFoundError):
            self.executor.execute_and_return_result(code)

    def test_execute_and_return_result_with_plot(self):
        """Test execution with a plot result."""
        code = "result = {'type': 'plot', 'value': 'my_plot'}"
        self.executor.execute(code)
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, {"type": "plot", "value": "my_plot"})

    def test_get_variable_last_line_of_code_assignment(self):
        """Test extracting variable name from an assignment."""
        code = "a = 5\nb = 10\nresult = a + b"
        var_name, subscript = self.executor._get_variable_last_line_of_code(code)
        self.assertEqual(var_name, "result")
        self.assertEqual(subscript, None)

    def test_get_variable_last_line_of_code_expression(self):
        """Test extracting variable name from an expression."""
        code = "print(5)\nresult = 5 + 5"
        var_name, _ = self.executor._get_variable_last_line_of_code(code)
        self.assertEqual(var_name, "result")

    def test_get_variable_last_line_of_code_invalid(self):
        """Test handling of invalid code syntax."""
        code = "invalid syntax"
        var_name = self.executor._get_variable_last_line_of_code(code)
        self.assertIsNone(var_name)

    def test_get_assign_variable_with_name(self):
        """Test extracting variable name from an assignment node with a Name target."""
        assign_node = MagicMock()
        assign_node.targets = [MagicMock(spec=ast.Name)]
        assign_node.targets[0].id = "my_var"

        var_name, _ = self.executor._get_assign_variable(assign_node)
        self.assertEqual(var_name, "my_var")

    def test_get_assign_variable_with_subscript(self):
        """Test extracting variable name from an assignment node with a Subscript target."""
        assign_node = MagicMock()
        subscript_mock = MagicMock(spec=ast.Subscript)
        subscript_mock.value = MagicMock(spec=ast.Name)
        subscript_mock.value.id = "subscript_var"
        subscript_mock.slice = MagicMock(return_value=5)
        assign_node.targets = [subscript_mock]

        var_name, _ = self.executor._get_assign_variable(assign_node)
        self.assertEqual(var_name, "subscript_var")

    def test_get_expr_variable_with_name(self):
        """Test extracting variable name from an expression node with a Name value."""
        expr_node = MagicMock()
        expr_node.value = MagicMock(spec=ast.Name)
        expr_node.value.id = "my_expr"

        var_name, _ = self.executor._get_expr_variable(expr_node)
        self.assertEqual(var_name, "my_expr")

    def test_get_subscript_variable_with_name_and_slice(self):
        """Test extracting variable name from a subscript node with a Name value."""
        subscript_node = MagicMock(spec=ast.Subscript)

        subscript_node.value = MagicMock(spec=ast.Name)
        subscript_node.value.id = "my_var"

        subscript_node.slice = MagicMock()
        subscript_node.slice.value = 0

        variable_name, slice_value = self.executor._get_subscript_variable(
            subscript_node
        )

        self.assertEqual(variable_name, "my_var")
        self.assertEqual(slice_value, 0)

    def test_execute_with_syntax_error(self):
        """Test executing code that raises a syntax error."""
        code = "result = 5 +"
        with self.assertRaises(SyntaxError):
            self.executor.execute(code)


if __name__ == "__main__":
    unittest.main()
