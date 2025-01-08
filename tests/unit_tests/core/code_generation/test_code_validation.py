import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_validation import CodeRequirementValidator
from pandasai.exceptions import ExecuteSQLQueryNotUsed


class TestCodeRequirementValidator(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for CodeRequirementValidator."""
        self.context = MagicMock(spec=AgentState)
        self.context.config.direct_sql = False  # Default to False
        self.validator = CodeRequirementValidator(self.context)

    def test_validate_code_without_execute_sql_query(self):
        """Test validation when direct_sql is enabled but execute_sql_query is not used."""
        self.context.config.direct_sql = True  # Enable direct_sql
        code = "result = 5 + 5"  # Code without execute_sql_query

        with self.assertRaises(ExecuteSQLQueryNotUsed) as context:
            self.validator.validate(code)

        self.assertEqual(
            str(context.exception),
            "The code must execute SQL queries using the `execute_sql_query` function, which is already defined!",
        )

    def test_validate_code_with_execute_sql_query(self):
        """Test validation when execute_sql_query is used."""
        self.context.config.direct_sql = True  # Enable direct_sql
        code = "execute_sql_query('SELECT * FROM table')"  # Code with execute_sql_query

        result = self.validator.validate(code)
        self.assertTrue(result)

    def test_validate_code_with_no_direct_sql(self):
        """Test validation when direct_sql is disabled."""
        self.context.config.direct_sql = False  # Disable direct_sql
        code = "result = 5 + 5"  # Any code should pass

        result = self.validator.validate(code)
        self.assertTrue(result)

    def test_validate_code_with_function_calls(self):
        """Test validation with various function calls."""
        self.context.config.direct_sql = True  # Enable direct_sql
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
        self.context.config.direct_sql = True  # Enable direct_sql
        code = """
import pandas as pd
df = pd.DataFrame()
execute_sql_query('SELECT * FROM table')
"""  # Code with pandas and execute_sql_query

        result = self.validator.validate(code)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
