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

import inspect
import time
import sys
from typing import List
import logging
from .path import find_closest
from pydantic import BaseModel


class Log(BaseModel):
    """Log class"""

    msg: str
    level: int


class Logger:
    """Logger class"""

    _logs: List[Log]
    _logger: logging.Logger
    _verbose: bool
    _last_time: float

    def __init__(self, save_logs: bool = True, verbose: bool = False):
        """Initialize the logger"""
        self._logs = []
        self._verbose = verbose
        self._last_time = time.time()

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

        self._logs.append(
            {
                "msg": message,
                "level": logging.getLevelName(level),
                "time": self._calculate_time_diff(),
                "source": self._invoked_from(),
            }
        )

    def _invoked_from(self, level: int = 5) -> str:
        """Return the name of the class that invoked the logger"""
        calling_class = None
        for frame_info in inspect.stack()[1:]:
            frame_locals = frame_info[0].f_locals
            calling_instance = frame_locals.get("self")
            if calling_instance and calling_instance.__class__ != self.__class__:
                calling_class = calling_instance.__class__.__name__
                break
            level -= 1
            if level <= 0:
                break
        return calling_class

    def _calculate_time_diff(self):
        """Calculate the time difference since the last log"""
        time_diff = time.time() - self._last_time
        self._last_time = time.time()
        return time_diff

    @property
    def logs(self) -> List[str]:
        """Return the logs"""
        return self._logs

    @property
    def verbose(self) -> bool:
        """Return the verbose flag"""
        return self._verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        """Set the verbose flag"""
        self._verbose = verbose
        self._logger.handlers = []
        if verbose:
            self._logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            # remove the StreamHandler if it exists
            for handler in self._logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    self._logger.removeHandler(handler)

    @property
    def save_logs(self) -> bool:
        """Return the save_logs flag"""
        return len(self._logger.handlers) > 0

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        """Set the save_logs flag"""
        if save_logs and not self.save_logs:
            filaname = find_closest("pandasai.log")
            self._logger.addHandler(logging.FileHandler(filaname))
        elif not save_logs and self.save_logs:
            # remove the FileHandler if it exists
            for handler in self._logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    self._logger.removeHandler(handler)
