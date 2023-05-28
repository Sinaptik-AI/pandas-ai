""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""

from pandasai.exceptions import MethodNotImplementedError


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

    def __str__(self):
        if self.text is None:
            raise MethodNotImplementedError

        return self.text.format(**self._args)
