from pandasai.helpers.logger import Logger
from pandasai.schemas.df_config import Config


class Context:
    """
    Context class that contains context from SmartDataLake for ResponseParsers
    Context contain the application config, logger and engine( pandas, polars etc).
    """

    _config = None
    _logger = None
    _engine: str = None

    def __init__(
        self, config: Config, logger: Logger = None, engine: str = None
    ) -> None:
        self._config = config
        self._logger = logger
        self._engine = engine

    @property
    def config(self):
        """Getter for _config attribute."""
        return self._config

    @property
    def logger(self):
        """Getter for _logger attribute."""
        return self._logger

    @property
    def engine(self):
        """Getter for _engine attribute."""
        return self._engine
