from pandasai.helpers.logger import Logger
from pandasai.schemas.df_config import Config


class Context:
    _config = None
    _logger = None
    _engine: str = None

    def __init__(self, config: Config, logger=Logger, engine: str = None) -> None:
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
        """Getter for _logger attribute."""
        return self._engine
