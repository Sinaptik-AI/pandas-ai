from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional, Generator

from openai.openai_object import OpenAIObject

MODEL_COST_PER_1K_TOKENS = {
    # GPT-4 input
    "gpt-4": 0.03,
    "gpt-4-0613": 0.03,
    "gpt-4-32k": 0.06,
    "gpt-4-32k-0613": 0.06,
    # GPT-4 output
    "gpt-4-completion": 0.06,
    "gpt-4-0613-completion": 0.06,
    "gpt-4-32k-completion": 0.12,
    "gpt-4-32k-0613-completion": 0.12,
    # GPT-3.5 input
    "gpt-3.5-turbo": 0.0015,
    "gpt-3.5-turbo-0613": 0.0015,
    "gpt-3.5-turbo-instruct": 0.0015,
    "gpt-3.5-turbo-16k": 0.003,
    "gpt-3.5-turbo-16k-0613": 0.003,
    # GPT-3.5 output
    "gpt-3.5-turbo-completion": 0.002,
    "gpt-3.5-turbo-0613-completion": 0.002,
    "gpt-3.5-turbo-instruct-completion": 0.002,
    "gpt-3.5-turbo-16k-completion": 0.004,
    "gpt-3.5-turbo-16k-0613-completion": 0.004,
    # Azure GPT-35 input
    "gpt-35-turbo": 0.0015,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613": 0.0015,
    "gpt-35-turbo-instruct": 0.0015,
    "gpt-35-turbo-16k": 0.003,
    "gpt-35-turbo-16k-0613": 0.003,
    # Azure GPT-35 output
    "gpt-35-turbo-completion": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613-completion": 0.002,
    "gpt-35-turbo-instruct-completion": 0.002,
    "gpt-35-turbo-16k-completion": 0.004,
    "gpt-35-turbo-16k-0613-completion": 0.004,
    # Others
    "text-davinci-003": 0.02,
}


def get_openai_token_cost_for_model(
        model_name: str,
        num_tokens: int,
        is_completion: bool = False,
) -> float:
    """
    Get the cost in USD for a given model and number of tokens.

    Args:
        model_name (str): Name of the model
        num_tokens (int): Number of tokens.
        is_completion: Whether `num_tokens` refers to completion tokens or not.
            Defaults to False.

    Returns:
        float: Cost in USD.
    """
    model_name = model_name.lower()
    if is_completion and (
            model_name.startswith("gpt-4")
            or model_name.startswith("gpt-3.5")
            or model_name.startswith("gpt-35")
    ):
        # The cost of completion token is different from
        # the cost of prompt tokens.
        model_name = model_name + "-completion"
    if model_name not in MODEL_COST_PER_1K_TOKENS:
        raise ValueError(
            f"Unknown model: {model_name}. Please provide a valid OpenAI model name."
            "Known models are: " + ", ".join(MODEL_COST_PER_1K_TOKENS.keys())
        )
    return MODEL_COST_PER_1K_TOKENS[model_name] * (num_tokens / 1000)


class OpenAICallbackHandler:
    """Callback Handler that tracks OpenAI info."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Total Cost (USD): ${self.total_cost:9.6f}"
        )

    def __call__(self, response: OpenAIObject) -> None:
        """Collect token usage"""
        usage = response.usage
        if "total_tokens" not in usage:
            return None

        model_name = response.model
        if model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(
                model_name, usage.prompt_tokens
            )
            completion_cost = get_openai_token_cost_for_model(
                model_name, usage.completion_tokens, is_completion=True
            )
            self.total_cost += prompt_cost + completion_cost

        self.total_tokens += usage.total_tokens
        self.prompt_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens

    def __copy__(self) -> "OpenAICallbackHandler":
        """Return a copy of the callback handler."""
        return self


openai_callback_var: ContextVar[Optional[OpenAICallbackHandler]] = ContextVar(
    "openai_callback", default=None
)


@contextmanager
def get_openai_callback() -> Generator[OpenAICallbackHandler, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Yields:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with get_openai_callback() as cb:
        ...     # Use the OpenAI callback handler
    """
    cb = OpenAICallbackHandler()
    openai_callback_var.set(cb)
    yield cb
    openai_callback_var.set(None)
