from ..schemas.df_config import Config
from typing import Union, Optional
from pandasai.responses.context import Context
from ..helpers.logger import Logger
from pandasai.responses.response_parser import ResponseParser
from abc import ABC, abstractmethod


class BaseLogic(ABC):
    """
    Logic units for pipeline.
    """

    def __init__(self):
        pass

    @abstractmethod
    def call(self, input_):
        """
        This method will return output according to
        Implementation."""
        pass


class PromptRequestLogic(BaseLogic):
    """
    Logic units for pipeline.
    """

    def __init__(self):
        pass

    def call(self,input_):
        """
        This method will return output according to
        implementation.
        """
        pass


class Pipeline:
    """
    Base Pipeline class to be extended for other pipelines.
    """

    _config: Config = None
    _logger: Logger
    _logics: list(BaseLogic)

    def __init__(
        self,
        config: Union[Config, dict] = None,
        context: Optional[Context] = None,
        logics: Optional(list(PromptRequestLogic)) = None,
    ):
        """
        Intialize the pipeline with given context and configuration
            parameters.

        Args :
            context (Context) : Context is required for ResponseParsers.
            config (dict) : The configuration to pipeline.
        """

        if isinstance(config, dict):
            config = Config(**config)

        self._config = config

        self._logger = Logger(
            save_logs=self._config.save_logs, verbose=self._config.verbose
        )
        if not context:
            context = Context(self._config, self.logger, self.engine)

        if self._config.response_parser:
            self._response_parser = self._config.response_parser(context)
        else:
            self._response_parser = ResponseParser(context)

    @abstractmethod
    def execute(self):
        """
        This functions is responsible to loop through logic and
            Implementation.
        """
        pass
