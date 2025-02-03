from unittest.mock import Mock, patch

import pytest

from pandasai.core.prompts import GeneratePythonCodeWithSQLPrompt


@pytest.fixture
def mock_context():
    context = Mock()
    context.memory = Mock()
    context.memory.to_json.return_value = {"history": []}
    context.memory.agent_description = "Test Agent Description"
    context.dfs = [Mock()]
    context.dfs[0].to_json.return_value = {"name": "test_df", "data": []}
    context.config.direct_sql = True
    return context


def test_to_json(mock_context):
    """Test that to_json returns the expected structure with all required fields"""
    prompt = GeneratePythonCodeWithSQLPrompt(context=mock_context, output_type="code")

    # Mock the to_string method
    with patch.object(prompt, "to_string", return_value="test prompt"):
        result = prompt.to_json()

        assert isinstance(result, dict)
        assert "datasets" in result
        assert isinstance(result["datasets"], list)
        assert len(result["datasets"]) == 1
        assert result["datasets"][0] == {"name": "test_df", "data": []}

        assert "conversation" in result
        assert result["conversation"] == {"history": []}

        assert "system_prompt" in result
        assert result["system_prompt"] == "Test Agent Description"

        assert "prompt" in result
        assert result["prompt"] == "test prompt"

        assert "config" in result
        assert isinstance(result["config"], dict)
        assert "direct_sql" in result["config"]
        assert result["config"]["direct_sql"] is True
        assert "output_type" in result["config"]
        assert result["config"]["output_type"] == "code"
