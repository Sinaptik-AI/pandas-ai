from unittest.mock import MagicMock, patch

import pytest
from jinja2 import Environment

from pandasai.core.prompts.base import BasePrompt


class TestBasePrompt:
    def test_to_json_without_context(self):
        # Given a BasePrompt instance without context
        class TestPrompt(BasePrompt):
            template = "Test template {{ var }}"

        prompt = TestPrompt(var="value")

        # When calling to_json
        result = prompt.to_json()

        # Then it should return a dict with only the prompt
        assert isinstance(result, dict)
        assert list(result.keys()) == ["prompt"]
        assert result["prompt"] == "Test template value"

    def test_to_json_with_context(self):
        # Given a BasePrompt instance with context
        class TestPrompt(BasePrompt):
            template = "Test template {{ var }}"

        memory = MagicMock()
        memory.to_json.return_value = ["conversation1", "conversation2"]
        memory.agent_description = "test agent"

        context = MagicMock()
        context.memory = memory

        prompt = TestPrompt(var="value", context=context)

        # When calling to_json
        result = prompt.to_json()

        # Then it should return a dict with conversation, system_prompt and prompt
        assert isinstance(result, dict)
        assert set(result.keys()) == {"conversation", "system_prompt", "prompt"}
        assert result["conversation"] == ["conversation1", "conversation2"]
        assert result["system_prompt"] == "test agent"
        assert result["prompt"] == "Test template value"

    def test_render_with_variables(self):
        # Given a BasePrompt instance with a template containing variables
        class TestPrompt(BasePrompt):
            template = "Hello {{ name }}!\nHow are you?\n\n\n\nGoodbye {{ name }}!"

        prompt = TestPrompt(name="World")

        # When calling render
        result = prompt.render()

        # Then it should:
        # 1. Replace variables correctly
        # 2. Remove extra newlines (more than 2)
        expected = "Hello World!\nHow are you?\n\nGoodbye World!"
        assert result == expected

    def test_render_with_template_path(self):
        # Given a BasePrompt instance with a template path
        class TestPrompt(BasePrompt):
            template_path = "test_template.txt"

        with patch.object(Environment, "get_template") as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = "Hello\n\n\n\nWorld!"
            mock_get_template.return_value = mock_template

            prompt = TestPrompt(name="Test")

            # When calling render
            result = prompt.render()

            # Then it should:
            # 1. Use the template from file
            # 2. Remove extra newlines
            assert result == "Hello\n\nWorld!"
            mock_template.render.assert_called_once_with(name="Test")
