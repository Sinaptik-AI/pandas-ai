"""PandasAI's custom exceptions.

This module contains the implementation of Custom Exceptions.

"""


class InvalidRequestError(Exception):
    """
    Raised when the request is not successful.

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


class NoResultFoundError(Exception):
    """
    Raised when no result is found in the response.

    Args:
        Exception (Exception): NoResultFoundError
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
    Raised when deployment name is not passed to azure as it's a required parameter

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


class UnSupportedLogicUnit(Exception):
    """
    Raised when unsupported logic unit is added in the pipeline
    Args:
        Exception (Exception): UnSupportedLogicUnit
    """


class InvalidWorkspacePathError(Exception):
    """
    Raised when the environment variable of workspace exist but path is invalid

    Args:
        Exception (Exception): InvalidWorkspacePathError
    """


class InvalidConfigError(Exception):
    """
    Raised when config value is not applicable
    Args:
        Exception (Exception): InvalidConfigError
    """


class MaliciousQueryError(Exception):
    """
    Raise error if malicious query is generated
    Args:
        Exception (Exception): MaliciousQueryError
    """


class InvalidLLMOutputType(Exception):
    """
    Raise error if the output type is invalid
    Args:
        Exception (Exception): InvalidLLMOutputType
    """


class ExecuteSQLQueryNotUsed(Exception):
    """
    Raise error if Execute SQL Query is not used
    Args:
        Exception (Exception): ExecuteSQLQueryNotUsed
    """


class MissingVectorStoreError(Exception):
    """
    Raise error if vector store is not found
    Args:
        Exception (Exception): MissingVectorStoreError
    """


class PandasAIApiKeyError(Exception):
    """
    Raise error if api key is not found for remote vectorstore and llm
    Args:
        Exception (Exception): PandasAIApiKeyError
    """

    def __init__(self):
        message = (
            "The api_key client option must be set either by passing api_key to the client "
            "or by setting the PANDASAI_API_KEY environment variable. To get the key follow below steps:\n"
            "1. Go to https://www.pandabi.ai and sign up\n"
            "2. From settings go to API keys and copy\n"
            "3. Set environment variable like os.environ['PANDASAI_API_KEY'] = '$2a$10$flb7....'"
        )
        super().__init__(message)


class PandasAIApiCallError(Exception):
    """
    Raise error if exception in API request fails
    Args:
        Exception (Exception): PandasAIApiCallError
    """
