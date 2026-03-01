from unittest.mock import Mock, patch

import pytest

from pandasai.core.prompts import GeneratePythonCodeWithSQLPrompt
from pandasai.helpers.memory import Memory


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


@pytest.fixture
def render_context():
    """Context with real Memory for template rendering tests."""
    context = Mock()
    context.dfs = []
    context.skills = []
    context.config.direct_sql = True
    context.vectorstore = None
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


def test_template_includes_previous_conversation(render_context):
    """Test that the rendered template includes previous conversation history."""
    memory = Memory(memory_size=10)
    memory.add("What is the average salary?", is_user=True)
    memory.add('result = {"type": "number", "value": 50000}', is_user=False)
    memory.add("Show me the top 5 earners", is_user=True)
    render_context.memory = memory

    prompt = GeneratePythonCodeWithSQLPrompt(
        context=render_context, last_code_generated=None, output_type="number"
    )
    rendered = prompt.to_string()

    assert "PREVIOUS CONVERSATION" in rendered
    assert "average salary" in rendered
    assert "top 5 earners" in rendered


def test_template_no_previous_conversation_for_single_message(render_context):
    """Test that single-message memory does not show PREVIOUS CONVERSATION."""
    memory = Memory(memory_size=10)
    memory.add("What is the average salary?", is_user=True)
    render_context.memory = memory

    prompt = GeneratePythonCodeWithSQLPrompt(
        context=render_context, last_code_generated=None, output_type="number"
    )
    rendered = prompt.to_string()

    assert "PREVIOUS CONVERSATION" not in rendered
    assert "average salary" in rendered
