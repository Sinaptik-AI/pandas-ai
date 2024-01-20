from pandasai.helpers.logger import Logger
from pandasai.schemas.df_config import Config


class Context:
    """
    Context class that contains context from Agent for ResponseParsers
    Context contain the application config and logger.
    """

    _config = None
    _logger = None

    def __init__(self, config: Config, logger: Logger = None) -> None:
        self._config = config
        self._logger = logger

    @property
    def config(self):
        """Getter for _config attribute."""
        return self._config

    @property
    def logger(self):
        """Getter for _logger attribute."""
        return self._logger
