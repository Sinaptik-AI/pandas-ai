"""Unit tests for the base prompt class"""

import pytest

from pandasai.exceptions import MethodNotImplementedError
from pandasai.prompts.base import Prompt


class TestBasePrompt:
    """Unit tests for the base prompt class"""

    def test_text(self):
        """Test that the text attribute is required"""
        with pytest.raises(MethodNotImplementedError):
            print(Prompt())

    def test_str(self):
        """Test that the __str__ method is implemented"""

        class TestPrompt(Prompt):
            """Test prompt"""

            text = "Test prompt"

        assert str(TestPrompt()) == "Test prompt"

    def test_str_not_implemented(self):
        """Test that the __str__ method is implemented"""

        class TestPrompt(Prompt):
            """Test prompt"""

            pass

        with pytest.raises(MethodNotImplementedError):
            str(TestPrompt())

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        class TestPrompt(Prompt):
            """Test prompt"""

            text = "Test prompt {arg1} {arg2}"

        assert str(TestPrompt(arg1="arg1", arg2="arg2")) == "Test prompt arg1 arg2"

    def test_str_with_args_not_implemented(self):
        """Test that the __str__ method is implemented"""

        class TestPrompt(Prompt):
            """Test prompt"""

            text = "Test prompt {arg1} {arg2}"

        with pytest.raises(KeyError):
            str(TestPrompt())
