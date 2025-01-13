import unittest
from unittest.mock import MagicMock

from pandasai.config import Config
from pandasai.core.code_execution.code_executor import CodeExecutor
from pandasai.exceptions import CodeExecutionError, NoResultFoundError


class TestCodeExecutor(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock(specs=Config)
        self.executor = CodeExecutor(self.config)

    def test_initialization(self):
        """Test initialization of CodeExecutor."""
        self.assertIsInstance(self.executor._environment, dict)

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

    def test_execute_with_syntax_error(self):
        """Test executing code that raises a syntax error."""
        code = "result = 5 +"
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)


if __name__ == "__main__":
    unittest.main()
