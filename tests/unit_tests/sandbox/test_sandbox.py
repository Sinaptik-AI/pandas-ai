import unittest
from unittest.mock import MagicMock, patch

from pandasai.sandbox import Sandbox


class TestSandbox(unittest.TestCase):
    def setUp(self):
        class SandboxImpl(Sandbox):
            def start(self):
                self._started = True

            def stop(self):
                self._started = False

            def _exec_code(self, code: str, environment: dict) -> dict:
                exec_globals = environment.copy()
                exec(code, exec_globals)
                return exec_globals

            def pass_csv(self, csv_data):
                return f"Processed CSV: {csv_data}"

        self.sandbox = SandboxImpl()

    def test_start(self):
        self.assertFalse(self.sandbox._started)
        self.sandbox.start()
        self.assertTrue(self.sandbox._started)

    def test_stop(self):
        self.sandbox.start()
        self.assertTrue(self.sandbox._started)
        self.sandbox.stop()
        self.assertFalse(self.sandbox._started)

    def test_execute_calls_start_if_not_started(self):
        code = "a = 10"
        environment = {}
        result = self.sandbox.execute(code, environment)
        self.assertIn("a", result)
        self.assertEqual(result["a"], 10)
        self.assertTrue(self.sandbox._started)

    def test_execute_does_not_call_start_if_already_started(self):
        code = "a = 20"
        environment = {}
        self.sandbox.start()
        with patch.object(
            self.sandbox, "start", wraps=self.sandbox.start
        ) as mock_start:
            result = self.sandbox.execute(code, environment)
            mock_start.assert_not_called()
        self.assertIn("a", result)
        self.assertEqual(result["a"], 20)

    def test_pass_csv(self):
        result = self.sandbox.pass_csv("sample_data")
        self.assertEqual(result, "Processed CSV: sample_data")

    def test_extract_sql_queries(self):
        code = """
query = "SELECT * FROM users"
def execute_sql_query(sql):
    return sql
execute_sql_query("SELECT id FROM orders")
        """
        queries = self.sandbox._extract_sql_queries_from_code(code)
        self.assertEqual(queries, ["SELECT * FROM users", "SELECT id FROM orders"])

    def test_extract_single_sql_queries(self):
        code = """
query = "SELECT * FROM users"
execute_sql_query(query)
        """
        queries = self.sandbox._extract_sql_queries_from_code(code)
        self.assertEqual(queries, ["SELECT * FROM users"])

    def test_compile_code_valid(self):
        code = "x = 5\ny = 10\nresult = x + y"
        compiled = self.sandbox._compile_code(code)
        self.assertIsNotNone(compiled)

    def test_compile_code_invalid(self):
        code = "x = 5\ny ="
        with self.assertRaises(SyntaxError) as context:
            self.sandbox._compile_code(code)
        self.assertIn("Syntax error in code", str(context.exception))

    def test_not_implemented_methods(self):
        sandbox_base = Sandbox()
        with self.assertRaises(NotImplementedError):
            sandbox_base.start()
        with self.assertRaises(NotImplementedError):
            sandbox_base.stop()
        with self.assertRaises(NotImplementedError):
            sandbox_base._exec_code("", {})
        with self.assertRaises(NotImplementedError):
            sandbox_base.pass_csv("data")


if __name__ == "__main__":
    unittest.main()
