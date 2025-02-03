from unittest.mock import Mock, patch

import pytest

from pandasai.core.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)


def test_to_json():
    # Mock the necessary dependencies
    mock_memory = Mock()
    mock_memory.to_json.return_value = {"conversations": "test"}
    mock_memory.agent_description = "test agent"

    mock_dataset = Mock()
    mock_dataset.to_json.return_value = {"data": "test data"}

    mock_context = Mock()
    mock_context.memory = mock_memory
    mock_context.dfs = [mock_dataset]

    # Create test data
    props = {
        "context": mock_context,
        "code": "test code",
        "error": Exception("test error"),
        "output_type": "test_type",
    }

    # Create instance of prompt
    prompt = CorrectOutputTypeErrorPrompt(**props)

    # Call to_json method
    result = prompt.to_json()

    # Verify the structure and content of the result
    assert isinstance(result, dict)
    assert "datasets" in result
    assert "conversation" in result
    assert "system_prompt" in result
    assert "error" in result
    assert "config" in result

    # Verify specific values
    assert result["datasets"] == [{"data": "test data"}]
    assert result["conversation"] == {"conversations": "test"}
    assert result["system_prompt"] == "test agent"
    assert result["error"] == {
        "code": "test code",
        "error_trace": "test error",
        "exception_type": "InvalidLLMOutputType",
    }
    assert result["config"] == {"output_type": "test_type"}

    # Verify that the mock methods were called
    mock_memory.to_json.assert_called_once()
    mock_dataset.to_json.assert_called_once()
