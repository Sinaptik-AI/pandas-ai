"""Unit tests for generate response prompt class"""

from datetime import date

import pytest

from pandasai.prompts.generate_response import GenerateResponsePrompt


class TestCorrectErrorPrompt:
    """Unit tests for generate response prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""
        assert (
            str(
                GenerateResponsePrompt(
                    question="What is the correct code?",
                    error_message="Error message",
                    code="df.head()",
                    answer="df.head(5)",
                    num_rows=5,
                    num_columns=5,
                    rows_to_display=5,
                    df_head="df.head()",
                    error_returned="error",
                )
            )
            == f"""
Question: What is the correct code?
Answer: df.head(5)

Rewrite the answer to the question in a conversational way.
"""
        )
