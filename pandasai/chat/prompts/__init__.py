from __future__ import annotations
from typing import TYPE_CHECKING
from pandasai.chat.prompts.correct_execute_sql_query_usage_error_prompt import (
    CorrectExecuteSQLQueryUsageErrorPrompt,
)
from pandasai.chat.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)
from .generate_python_code_with_sql import GeneratePythonCodeWithSQLPrompt
from .base import BasePrompt
from .correct_error_prompt import CorrectErrorPrompt
from .generate_python_code import GeneratePythonCodePrompt

if TYPE_CHECKING:
    from pandasai.agent.state import AgentState


def get_chat_prompt(context: AgentState) -> BasePrompt:
    viz_lib = "matplotlib"
    if context.config.data_viz_library:
        viz_lib = context.config.data_viz_library

    return GeneratePythonCodePrompt(
        context=context,
        last_code_generated=context.get("last_code_generated"),
        viz_lib=viz_lib,
        output_type=context.output_type,
    )


def get_chat_prompt_for_sql(context: AgentState) -> BasePrompt:
    viz_lib = "matplotlib"
    if context.config.data_viz_library:
        viz_lib = context.config.data_viz_library

    return GeneratePythonCodeWithSQLPrompt(
        context=context,
        last_code_generated=context.get("last_code_generated"),
        viz_lib=viz_lib,
        output_type=context.output_type,
    )


def get_correct_error_prompt(
    context: AgentState, code: str, traceback_error: str
) -> BasePrompt:
    return CorrectErrorPrompt(
        context=context,
        code=code,
        error=traceback_error,
    )


def get_correct_error_prompt_for_sql(
    context: AgentState, code: str, traceback_error: str
) -> BasePrompt:
    return CorrectExecuteSQLQueryUsageErrorPrompt(
        context=context, code=code, error=traceback_error
    )


def get_correct_output_type_error_prompt(
    context: AgentState, code: str, traceback_error: str
) -> BasePrompt:
    return CorrectOutputTypeErrorPrompt(
        context=context,
        code=code,
        error=traceback_error,
        output_type=context.output_type,
    )


__all__ = [
    "BasePrompt",
    "CorrectErrorPrompt",
    "GeneratePythonCodePrompt",
    "GeneratePythonCodeWithSQLPrompt",
]
