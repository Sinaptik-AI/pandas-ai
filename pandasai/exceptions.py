"""PandasAI's custom exceptions."""


class APIKeyNotFoundError(Exception):
    """Raised when the API key is not defined/declared."""


class LLMNotFoundError(Exception):
    """Raised when the LLM is not provided"""


class NoCodeFoundError(Exception):
    """Raised when no code is found in the response"""


class MethodNotImplementedError(Exception):
    """Raised when a method is not implemented"""


class UnsupportedOpenAIModelError(Exception):
    """Raised when an unsupported OpenAI model is used"""
