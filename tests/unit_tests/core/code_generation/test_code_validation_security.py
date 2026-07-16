import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_validation import (
    _DANGEROUS_MODULES,
    CodeRequirementValidator,
)
from pandasai.exceptions import MaliciousCodeGenerated


class TestSecurityVisitor(unittest.TestCase):
    """Security tests for the _SecurityVisitor in CodeRequirementValidator."""

    def setUp(self):
        self.context = MagicMock(spec=AgentState)
        self.validator = CodeRequirementValidator(self.context)

    def _validate(self, code):
        """Helper that runs security validation only (skips execute_sql_query check)."""
        import ast

        from pandasai.core.code_generation.code_validation import (
            CodeRequirementValidator,
        )

        tree = ast.parse(code)
        visitor = CodeRequirementValidator._SecurityVisitor()
        visitor.visit(tree)

    def test_blocks_import_os(self):
        """import os should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("import os")

    def test_blocks_import_os_submodule(self):
        """import os.path should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("import os.path")

    def test_blocks_import_subprocess(self):
        """import subprocess should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("import subprocess")

    def test_blocks_from_os_import(self):
        """from os import system should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("from os import system")

    def test_blocks_from_os_path_import(self):
        """from os.path import join should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("from os.path import join")

    def test_blocks_from_subprocess_import(self):
        """from subprocess import Popen should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("from subprocess import Popen")

    def test_blocks_dunder_import_call(self):
        """__import__('os') should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = __import__("os")')

    def test_blocks_builtins_dunder_import(self):
        """builtins.__import__('os') should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = builtins.__import__("os")')

    def test_blocks_os_system_attribute_access(self):
        """os.system(...) should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = os.system("ls")')

    def test_blocks_os_popen_attribute_access(self):
        """os.popen(...) should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = os.popen("ls")')

    def test_blocks_subprocess_popen(self):
        """subprocess.Popen(...) should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = subprocess.Popen(["ls"])')

    def test_blocks_nested_attribute_access(self):
        """os.path.join should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('x = os.path.join("a", "b")')

    def test_blocks_sys_exit(self):
        """sys.exit should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("sys.exit(0)")

    def test_blocks_shutil_rmtree(self):
        """shutil.rmtree should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('shutil.rmtree("/tmp/dir")')

    def test_blocks_socket_connection(self):
        """socket.socket should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("s = socket.socket()")

    def test_blocks_importlib_import_module(self):
        """importlib.import_module should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate('importlib.import_module("os")')

    def test_blocks_builtins_import(self):
        """import builtins should raise MaliciousCodeGenerated."""
        with self.assertRaises(MaliciousCodeGenerated):
            self._validate("import builtins")

    def test_all_dangerous_modules_blocked(self):
        """Every module in _DANGEROUS_MODULES should be blocked via import."""
        for module in _DANGEROUS_MODULES:
            with self.subTest(module=module):
                with self.assertRaises(MaliciousCodeGenerated):
                    self._validate(f"import {module}")

    def test_all_dangerous_modules_blocked_from_import(self):
        """Every module in _DANGEROUS_MODULES should be blocked via from import."""
        for module in _DANGEROUS_MODULES:
            with self.subTest(module=module):
                with self.assertRaises(MaliciousCodeGenerated):
                    self._validate(f"from {module} import something")

    def test_all_dangerous_modules_blocked_attribute_access(self):
        """Every module in _DANGEROUS_MODULES should be blocked via attribute access."""
        for module in _DANGEROUS_MODULES:
            with self.subTest(module=module):
                with self.assertRaises(MaliciousCodeGenerated):
                    self._validate(f"x = {module}.something()")

    def test_allows_pandas_import(self):
        """import pandas should not raise."""
        try:
            self._validate("import pandas")
        except MaliciousCodeGenerated:
            self.fail("import pandas should not be blocked")

    def test_allows_numpy_import(self):
        """import numpy should not raise."""
        try:
            self._validate("import numpy")
        except MaliciousCodeGenerated:
            self.fail("import numpy should not be blocked")

    def test_allows_matplotlib_import(self):
        """import matplotlib should not raise."""
        try:
            self._validate("import matplotlib")
        except MaliciousCodeGenerated:
            self.fail("import matplotlib should not be blocked")

    def test_allows_seaborn_import(self):
        """import seaborn should not raise."""
        try:
            self._validate("import seaborn")
        except MaliciousCodeGenerated:
            self.fail("import seaborn should not be blocked")

    def test_allows_duckdb_import(self):
        """import duckdb should not raise."""
        try:
            self._validate("import duckdb")
        except MaliciousCodeGenerated:
            self.fail("import duckdb should not be blocked")

    def test_allows_safe_function_calls(self):
        """Safe function calls like len(), print(), type() should not raise."""
        try:
            self._validate("x = len([1, 2, 3])")
            self._validate('x = type("hello")')
            self._validate("x = isinstance(1, int)")
        except MaliciousCodeGenerated:
            self.fail("Safe function calls should not be blocked")

    def test_full_validate_with_execute_sql_query(self):
        """Full validate() should pass for legitimate code with execute_sql_query."""
        code = (
            'sql_query = "SELECT * FROM users"; result = execute_sql_query(sql_query)'
        )
        result = self.validator.validate(code)
        self.assertTrue(result)

    def test_full_validate_with_execute_sql_query_function_def(self):
        """Full validate() should pass for code defining execute_sql_query."""
        code = """
def execute_sql_query(query):
    return pd.DataFrame({"a": [1, 2, 3]})

sql_query = "SELECT * FROM users"
result = execute_sql_query(sql_query)
"""
        result = self.validator.validate(code)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
