"""
Base Middleware class

Middlewares are used to modify the code before it is executed.
"""

from abc import ABC, abstractmethod

from pandasai.exceptions import MethodNotImplementedError


class Middleware(ABC):
    """Base Middleware class"""

    _has_run: bool = False

    @abstractmethod
    def run(self, code: str) -> str:
        """Run the middleware"""
        raise MethodNotImplementedError

    def __call__(self, code) -> str:
        """Call the middleware"""
        self._has_run = True
        return self.run(code=code)

    @property
    def has_run(self) -> bool:
        """Return if the middleware has run"""
        return self._has_run
