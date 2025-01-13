import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.prompts import (
    get_chat_prompt_for_sql,
    get_correct_error_prompt_for_sql,
    get_correct_output_type_error_prompt,
)
from pandasai.core.prompts.base import BasePrompt
from pandasai.core.prompts.correct_execute_sql_query_usage_error_prompt import (
    CorrectExecuteSQLQueryUsageErrorPrompt,
)
from pandasai.core.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)


class TestChatPrompts(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for chat prompts."""
        self.context = MagicMock(spec=AgentState)
        memory = MagicMock()
        memory.count.return_value = 1
        self.context.memory = memory

    def test_get_chat_prompt_for_sql(self):
        """Test the get_chat_prompt_for_sql function."""
        self.context.output_type = "sql"

        prompt = get_chat_prompt_for_sql(self.context)

        self.assertIsInstance(prompt, BasePrompt)

    def test_get_correct_error_prompt_for_sql(self):
        """Test the get_correct_error_prompt_for_sql function."""
        code = "SELECT * FROM table"
        traceback_error = "SQL error"

        prompt = get_correct_error_prompt_for_sql(self.context, code, traceback_error)

        self.assertIsInstance(prompt, CorrectExecuteSQLQueryUsageErrorPrompt)

    def test_get_correct_output_type_error_prompt(self):
        """Test the get_correct_output_type_error_prompt function."""
        code = "some code"
        traceback_error = "Output type error"

        self.context.output_type = "expected_output_type"

        prompt = get_correct_output_type_error_prompt(
            self.context, code, traceback_error
        )

        self.assertIsInstance(prompt, CorrectOutputTypeErrorPrompt)


if __name__ == "__main__":
    unittest.main()
