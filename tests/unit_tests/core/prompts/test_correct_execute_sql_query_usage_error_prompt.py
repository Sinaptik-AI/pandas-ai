from unittest.mock import Mock, patch

import pytest

from pandasai.core.prompts.correct_execute_sql_query_usage_error_prompt import (
    CorrectExecuteSQLQueryUsageErrorPrompt,
)


def test_to_json():
    # Mock the dependencies
    mock_dataset = Mock()
    mock_dataset.to_json.return_value = {"mock_dataset": "data"}

    mock_memory = Mock()
    mock_memory.to_json.return_value = {"mock_conversation": "data"}
    mock_memory.agent_description = "Mock agent description"

    mock_context = Mock()
    mock_context.memory = mock_memory
    mock_context.dfs = [mock_dataset]

    # Create test data
    test_code = "SELECT * FROM table"
    test_error = Exception("Test error")

    # Create instance of the prompt class
    prompt = CorrectExecuteSQLQueryUsageErrorPrompt(
        context=mock_context,
        code=test_code,
        error=test_error,
    )

    # Call the method
    result = prompt.to_json()

    # Assertions
    assert result == {
        "datasets": [{"mock_dataset": "data"}],
        "conversation": {"mock_conversation": "data"},
        "system_prompt": "Mock agent description",
        "error": {
            "code": test_code,
            "error_trace": str(test_error),
            "exception_type": "ExecuteSQLQueryNotUsed",
        },
    }

    # Verify the mocks were called
    mock_dataset.to_json.assert_called_once()
    mock_memory.to_json.assert_called_once()
