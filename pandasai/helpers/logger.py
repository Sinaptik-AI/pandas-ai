"""
Logger class

This class is used to log messages to the console and/or a file.

Example:
    ```python
    from pandasai.helpers.logger import Logger

    logger = Logger()
    logger.log("Hello, world!")
    # 2021-08-01 12:00:00 [INFO] Hello, world!

    logger.logs
    #["Hello, world!"]
    ```
"""

import sys
from typing import List
import logging
from .path import find_closest


class Logger:
    """Logger class"""

    _logs: List[str]
    _logger: logging.Logger
    _verbose: bool

    def __init__(self, save_logs: bool = True, verbose: bool = False):
        """Initialize the logger"""
        self._logs = []
        self._verbose = verbose

        if save_logs:
            try:
                filaname = find_closest("pandasai.log")
            except ValueError:
                filaname = "pandasai.log"
            handlers = [logging.FileHandler(filaname)]
        else:
            handlers = []

        if verbose:
            handlers.append(logging.StreamHandler(sys.stdout))

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
        )
        self._logger = logging.getLogger(__name__)

    def log(self, message: str, level: int = logging.INFO):
        """Log a message"""

        if level == logging.INFO:
            self._logger.info(message)
        elif level == logging.WARNING:
            self._logger.warning(message)
        elif level == logging.ERROR:
            self._logger.error(message)
        elif level == logging.CRITICAL:
            self._logger.critical(message)

        self._logs.append({"msg": message, "level": level})

    @property
    def logs(self) -> List[str]:
        """Return the logs"""
        return self._logs

    @property
    def verbose(self) -> bool:
        """Return the verbose flag"""
        return self._verbose
