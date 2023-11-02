"""PandasAI's custom exceptions.

This module contains the implementation of Custom Exceptions.

"""


class InvalidRequestError(Exception):

    """
    Raised when the request is not succesfull.

    Args :
        Exception (Exception): InvalidRequestError
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


class UnsupportedModelError(Exception):
    """
    Raised when an unsupported model is used.

    Args:
        model_name (str): The name of the unsupported model.
        Exception (Exception): UnsupportedModelError
    """

    def __init__(self, model_name):
        self.model = model_name
        super().__init__(
            f"Unsupported model: The model '{model_name}' doesn't exist "
            f"or is not supported yet."
        )


class MissingModelError(Exception):
    """
    Raised when deployment name is not passed to azure as it's a required paramter

    Args:
    Exception (Exception): MissingModelError
    """


class LLMResponseHTTPError(Exception):
    """
    Raised when a remote LLM service responses with error HTTP code.

    Args:
        Exception (Exception): LLMResponseHTTPError
    """

    def __init__(self, status_code, error_msg=None):
        self.status_code = status_code
        self.error_msg = error_msg

        super().__init__(
            f"The remote server has responded with an error HTTP "
            f"code: {status_code}; {error_msg or ''}"
        )


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


class TemplateFileNotFoundError(FileNotFoundError):
    """
    Raised when a template file cannot be found.
    """

    def __init__(self, template_path, prompt_name="Unknown"):
        """
        __init__ method of TemplateFileNotFoundError Class

        Args:
            template_path (str): Path for template file.
            prompt_name (str): Prompt name. Defaults to "Unknown".
        """
        self.template_path = template_path
        super().__init__(
            f"Unable to find a file with template at '{template_path}' "
            f"for '{prompt_name}' prompt."
        )


class AdvancedReasoningDisabledError(Exception):
    """
    Raised when one tries to have access to the answer or reasoning without
    having use_advanced_reasoning_framework enabled.

    Args:
        Exception (Exception): AdvancedReasoningDisabledError
    """


class InvalidWorkspacePathError(Exception):
    """
    Raised when the environment variable of workspace exist but path is invalid

    Args:
        Exception (Exception): InvalidWorkspacePathError
    """
