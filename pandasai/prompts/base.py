""" Base class to implement a new Prompt """

from pandasai.exceptions import MethodNotImplementedError


class Prompt:
    """Base class to implement a new Prompt"""

    text = None
    _args = {}

    def __init__(self, **kwargs):
        if kwargs:
            self._args = kwargs

    def __str__(self):
        if self.text is None:
            raise MethodNotImplementedError

        return self.text.format(**self._args)
