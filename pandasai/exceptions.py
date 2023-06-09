"""PandasAI's custom exceptions.

This module contains the implementation of Custom Exceptions.

"""


class APIKeyNotFoundError(Exception):

    """
    Raised when the API key is not defined/declared.

    Args:
        Exception (Exception): APIKeyNotFoundError
    """


class LLMNotFoundError(Exception):
    """
    Raised when the LLM is not provided.

    Args:
        Exception (Exception): LLMNotFoundError
    """


class NoCodeFoundError(Exception):
    """
    Raised when no code is found in the response.

    Args:
        Exception (Exception): NoCodeFoundError
    """


class MethodNotImplementedError(Exception):
    """
    Raised when a method is not implemented.

    Args:
        Exception (Exception): MethodNotImplementedError
    """


class UnsupportedOpenAIModelError(Exception):
    """
    Raised when an unsupported OpenAI model is used.

    Args:
        Exception (Exception): UnsupportedOpenAIModelError
    """


class BadImportError(Exception):
    """
    Raised when a library not in the whitelist is imported.

    Args:
        Exception (Exception): BadImportError
    """

    def __init__(self, library_name):
        """
        __init__ method of BadImportError Class

        Args:
            library_name (str): Name of the library that is not in the whitelist.
        """
        self.library_name = library_name
        super().__init__(
            f"Generated code includes import of {library_name} which"
            " is not in whitelist."
        )
