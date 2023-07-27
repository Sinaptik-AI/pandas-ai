""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""

from pandasai.exceptions import MethodNotImplementedError
from string import Formatter


class Prompt:
    """Base class to implement a new Prompt"""

    text = None
    _args = {}

    def __init__(self, **kwargs):
        """
        __init__ method of Base class of Prompt Module
        Args:
            **kwargs: Inferred Keyword Arguments
        """
        if kwargs:
            self._args = kwargs

        """Set all the variables with underscore prefix with default value as DEFAULT
        This will prevent any possible key errors if anyone tries to print 
        prompt before running .run method"""
        if self.text:
            vars = [
                fn for _, fn, _, _ in Formatter().parse(self.text) if fn is not None
            ]
            for var in vars:
                if var[0] == "_" and var not in self._args:
                    self._args[var] = var

    def override_var(self, var, value):
        self._args[var] = value

    def __str__(self):
        if self.text is None:
            raise MethodNotImplementedError

        return self.text.format(**self._args)
