import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_security import CodeSecurityChecker
from pandasai.exceptions import MaliciousCodeGenerated


class TestCodeSecurityChecker(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for CodeSecurityChecker."""
        self.context = MagicMock(spec=AgentState)
        self.security_checker = CodeSecurityChecker(self.context)

    def test_is_malicious_code_with_dangerous_module(self):
        """Test detection of malicious code with a dangerous module."""
        code = "import os"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception), "Restricted library import detected: os"
        )

    def test_is_malicious_code_with_restricted_import(self):
        """Test detection of malicious code with a restricted import."""
        code = "from os import mkdir"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception), "Restricted library import detected: os"
        )

    def test_is_malicious_code_with_private_attribute_access(self):
        """Test detection of malicious code with private attribute access."""
        code = "obj._private_method()"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception),
            "Access to private attribute '_private_method' is not allowed.",
        )

    def test_is_jailbreak_with_dangerous_builtin(self):
        """Test detection of jailbreak methods."""
        code = "__import__('os')"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(str(context.exception), "Restricted builtins are used!")

    def test_is_unsafe_with_unsafe_method(self):
        """Test detection of unsafe operations."""
        code = "df.to_csv('file.csv')"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception),
            "The code is unsafe and can lead to I/O operations or other malicious operations that are not permitted!",
        )

    def test_check_with_safe_code(self):
        """Test that safe code passes without raising an error."""
        code = "x = 5 + 5"
        try:
            self.security_checker.check(code)
        except MaliciousCodeGenerated:
            self.fail("check() raised MaliciousCodeGenerated unexpectedly!")

    def test_check_with_multiple_checks(self):
        """Test multiple checks in one code block."""
        code = "import os\nx = 5\nobj._private_method()"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception), "Restricted library import detected: os"
        )

    def test_check_with_jailbreak_and_unsafe_methods(self):
        """Test detection of both jailbreak and unsafe methods in one code block."""
        code = "__import__('os')\ndf.to_excel('file.xlsx')"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(str(context.exception), "Restricted builtins are used!")

    def test_check_with_multiple_restricted_imports(self):
        """Test detection of multiple restricted imports."""
        code = "import os\nfrom restricted_lib import something"
        with self.assertRaises(MaliciousCodeGenerated) as context:
            self.security_checker.check(code)
        self.assertEqual(
            str(context.exception), "Restricted library import detected: os"
        )


if __name__ == "__main__":
    unittest.main()
