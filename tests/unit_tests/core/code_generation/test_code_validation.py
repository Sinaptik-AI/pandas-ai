import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_validation import CodeRequirementValidator
from pandasai.exceptions import ExecuteSQLQueryNotUsed


class TestCodeRequirementValidator(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for CodeRequirementValidator."""
        self.context = MagicMock(spec=AgentState)
        self.validator = CodeRequirementValidator(self.context)

    def test_validate_code_without_execute_sql_query(self):
        """Test validation when execute_sql_query is not used."""
        code = "result = 5 + 5"  # Code without execute_sql_query

        with self.assertRaises(ExecuteSQLQueryNotUsed) as context:
            self.validator.validate(code)

        self.assertEqual(
            str(context.exception),
            "The code must execute SQL queries using the `execute_sql_query` function, which is already defined!",
        )

    def test_validate_code_with_execute_sql_query(self):
        """Test validation when execute_sql_query is used."""
        code = "execute_sql_query('SELECT * FROM table')"  # Code with execute_sql_query

        result = self.validator.validate(code)
        self.assertTrue(result)

    def test_validate_code_with_function_calls(self):
        """Test validation with various function calls."""
        code = """
def some_function():
    pass
some_function()
execute_sql_query('SELECT * FROM table')
"""  # Code with a function call and execute_sql_query

        result = self.validator.validate(code)
        self.assertTrue(result)

    def test_validate_code_with_multiple_calls(self):
        """Test validation with multiple function calls."""
        code = """
import pandas as pd
df = pd.DataFrame()
execute_sql_query('SELECT * FROM table')
"""  # Code with pandas and execute_sql_query

        result = self.validator.validate(code)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
