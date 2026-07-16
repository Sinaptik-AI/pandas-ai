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


class TestCodeExecutorSecurity(unittest.TestCase):
    """Security tests to verify issues #1893 and #1895 are fixed."""

    def setUp(self):
        self.config = MagicMock(specs=Config)
        self.executor = CodeExecutor(self.config)

    def test_blocks_import_os(self):
        """Issue #1893: import os should be blocked at execution level."""
        code = (
            'import os; result = {"type": "string", "value": os.popen("whoami").read()}'
        )
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_import_subprocess(self):
        """Issue #1895: import subprocess should be blocked at execution level."""
        code = 'import subprocess; result = {"type": "string", "value": subprocess.check_output(["whoami"]).decode()}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_dunder_import(self):
        """Issue #1893: __import__() should be blocked at execution level."""
        code = 'result = {"type": "string", "value": __import__("os").popen("whoami").read()}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_open_call(self):
        """Issue #1895: open() should be blocked at execution level."""
        code = 'result = {"type": "string", "value": open("/etc/passwd").read()[:20]}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_eval_call(self):
        """Issue #1893: eval() should be blocked at execution level."""
        code = 'result = {"type": "string", "value": eval("__import__(\'os\').popen(\'whoami\').read().strip()")}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_exec_call(self):
        """Issue #1895: exec() should be blocked at execution level."""
        code = 'result = {"type": "string", "value": exec("import os; print(os.popen(\'whoami\').read())")}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_compile_call(self):
        """Issue #1893: compile() + exec() should be blocked."""
        code = 'result = {"type": "string", "value": eval(compile("import os", "", "exec"))}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_blocks_getattr_on_modules(self):
        """Issue #1895: getattr(os, "system") should be blocked."""
        code = 'result = {"type": "string", "value": getattr(__builtins__, "__import__")("os").popen("whoami").read()}'
        with self.assertRaises(CodeExecutionError):
            self.executor.execute(code)

    def test_legitimate_pandas_code_works(self):
        """Legitimate data analysis code should still work."""
        code = 'result = {"type": "number", "value": len(pd.DataFrame({"a": [1,2,3]}))}'
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result["value"], 3)

    def test_legitimate_arithmetic_works(self):
        """Arithmetic operations should still work."""
        code = "result = 10 + 20"
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, 30)

    def test_legitimate_list_operations_works(self):
        """List operations should still work."""
        code = "data = [1, 2, 3, 4, 5]; result = sum(data)"
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, 15)

    def test_legitimate_string_operations_works(self):
        """String operations should still work."""
        code = 'result = "hello world".upper()'
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, "HELLO WORLD")

    def test_legitimate_dict_operations_works(self):
        """Dict operations should still work."""
        code = 'data = {"a": 1, "b": 2, "c": 3}; result = data["b"]'
        result = self.executor.execute_and_return_result(code)
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
