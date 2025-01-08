import json

from .base_restricted_module import BaseRestrictedModule


class RestrictedJson(BaseRestrictedModule):
    def __init__(self):
        self.allowed_functions = [
            "load",
            "loads",
            "dump",
            "dumps",
        ]

        # Bind the allowed functions to the object
        for func in self.allowed_functions:
            if hasattr(json, func):
                setattr(self, func, self._wrap_function(getattr(json, func)))

    def __getattr__(self, name):
        if name not in self.allowed_functions:
            raise AttributeError(f"'{name}' is not allowed in RestrictedJson")
        return getattr(json, name)
