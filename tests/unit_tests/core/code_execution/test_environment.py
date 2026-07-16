import unittest
from unittest.mock import MagicMock, patch

from pandasai.core.code_execution.environment import (
    _get_restricted_builtins,
    get_environment,
    get_version,
    import_dependency,
)


class TestEnvironmentFunctions(unittest.TestCase):
    @patch("pandasai.core.code_execution.environment.import_dependency")
    def test_get_environment_with_secure_mode(self, mock_import_dependency):
        """Test get_environment function in secure mode."""
        mock_import_dependency.side_effect = lambda name: MagicMock(name=name)
        env = get_environment()

        self.assertIn("pd", env)
        self.assertIn("plt", env)
        self.assertIn("np", env)

    @patch("pandasai.core.code_execution.environment.import_dependency")
    def test_get_environment_without_secure_mode(self, mock_import_dependency):
        """Test get_environment function in non-secure mode."""
        mock_import_dependency.side_effect = lambda name: MagicMock(name=name)
        env = get_environment()

        self.assertIn("pd", env)
        self.assertIn("plt", env)
        self.assertIn("np", env)
        self.assertIsInstance(env["pd"], MagicMock)

    @patch("pandasai.core.code_execution.environment.importlib.import_module")
    def test_import_dependency_success(self, mock_import_module):
        """Test successful import of a dependency."""
        mock_import_module.return_value = MagicMock(__version__="1.0.0")
        module = import_dependency("numpy")

        self.assertIsNotNone(module)

    @patch("pandasai.core.code_execution.environment.importlib.import_module")
    def test_import_dependency_missing(self, mock_import_module):
        """Test handling of a missing dependency."""
        mock_import_module.side_effect = ImportError("Module not found")
        with self.assertRaises(ImportError):
            import_dependency("non_existent_module")

    @patch("pandasai.core.code_execution.environment.importlib.import_module")
    def test_import_dependency_with_extra_message(self, mock_import_module):
        """Test import dependency with additional error message."""
        mock_import_module.side_effect = ImportError("Module not found")
        with self.assertRaises(ImportError) as context:
            import_dependency("non_existent_module", extra="Please install it.")

        self.assertIn("Please install it.", str(context.exception))

    @patch("pandasai.core.code_execution.environment.importlib.import_module")
    def test_get_version_success(self, mock_import_module):
        """Test getting the version of a module successfully."""
        mock_import_module.return_value = MagicMock(__version__="1.0.0")
        version = get_version(mock_import_module("numpy"))
        self.assertEqual(version, "1.0.0")

    @patch("pandasai.core.code_execution.environment.importlib.import_module")
    def test_get_version_failure(self, mock_import_module):
        """Test getting version fails when __version__ is not present."""
        module_mock = MagicMock()
        module_mock.__name__ = "numpy"
        mock_import_module.return_value = module_mock
        with self.assertRaises(ImportError):
            get_version(mock_import_module("numpy"))


class TestRestrictedBuiltins(unittest.TestCase):
    def test_restricted_builtins_excludes_dangerous(self):
        """Test that restricted builtins exclude dangerous builtins."""
        builtins = _get_restricted_builtins()

        dangerous = [
            "open",
            "exec",
            "eval",
            "compile",
            "getattr",
            "setattr",
            "delattr",
            "globals",
            "locals",
            "vars",
            "dir",
            "breakpoint",
            "exit",
            "quit",
            "help",
            "input",
            "memoryview",
            "super",
            "staticmethod",
            "classmethod",
            "property",
            "bytearray",
            "bytes",
            "frozenset",
            "hash",
            "id",
            "callable",
            "next",
            "object",
        ]

        for name in dangerous:
            self.assertNotIn(
                name,
                builtins,
                f"Dangerous builtin '{name}' should not be in restricted builtins",
            )

    def test_restricted_builtins_includes_safe(self):
        """Test that restricted builtins include safe builtins needed for data analysis."""
        builtins = _get_restricted_builtins()

        safe = [
            "True",
            "False",
            "None",
            "int",
            "float",
            "str",
            "list",
            "dict",
            "tuple",
            "set",
            "bool",
            "type",
            "isinstance",
            "len",
            "range",
            "enumerate",
            "print",
            "Exception",
            "ValueError",
            "TypeError",
        ]

        for name in safe:
            self.assertIn(
                name,
                builtins,
                f"Safe builtin '{name}' should be in restricted builtins",
            )

    def test_get_environment_contains_restricted_builtins(self):
        """Test that get_environment returns an environment with restricted __builtins__."""
        env = get_environment()
        self.assertIn("__builtins__", env)
        self.assertIsInstance(env["__builtins__"], dict)
        self.assertNotIn("open", env["__builtins__"])
        self.assertNotIn("exec", env["__builtins__"])
        self.assertNotIn("eval", env["__builtins__"])
        self.assertIn("__import__", env["__builtins__"])
        self.assertIn("len", env["__builtins__"])

    def test_safe_import_blocks_dangerous_modules(self):
        """Test that the safe __import__ wrapper blocks dangerous modules."""
        from pandasai.core.code_execution.environment import _safe_import

        dangerous = ["os", "sys", "subprocess", "shutil", "socket", "pickle"]
        for module in dangerous:
            with self.subTest(module=module):
                with self.assertRaises(ImportError):
                    _safe_import(module)

    def test_safe_import_allows_safe_modules(self):
        """Test that the safe __import__ wrapper allows safe modules."""
        from pandasai.core.code_execution.environment import _safe_import

        safe = ["pandas", "numpy", "math", "json", "re", "datetime"]
        for module in safe:
            with self.subTest(module=module):
                try:
                    result = _safe_import(module)
                    self.assertIsNotNone(result)
                except ImportError as e:
                    if "is not allowed" in str(e):
                        self.fail(f"Safe module '{module}' was incorrectly blocked")
                    # Other ImportError (module not installed) is acceptable


if __name__ == "__main__":
    unittest.main()
