import base64

from .base_restricted_module import BaseRestrictedModule


class RestrictedBase64(BaseRestrictedModule):
    def __init__(self):
        self.allowed_functions = [
            "b64encode",  # Safe function to encode data into base64
            "b64decode",  # Safe function to decode base64 encoded data
        ]

        # Bind the allowed functions to the object
        for func in self.allowed_functions:
            if hasattr(base64, func):
                setattr(self, func, self._wrap_function(getattr(base64, func)))

    def __getattr__(self, name):
        if name not in self.allowed_functions:
            raise AttributeError(f"'{name}' is not allowed in RestrictedBase64")
        return getattr(base64, name)
