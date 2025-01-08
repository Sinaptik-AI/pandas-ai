class BaseRestrictedModule:
    def _wrap_function(self, func):
        def wrapper(*args, **kwargs):
            # Check for any suspicious arguments that might be used for importing
            for arg in args + tuple(kwargs.values()):
                if isinstance(arg, str):
                    # Check if the string is exactly one of the restricted modules
                    restricted_modules = ["io", "os", "subprocess", "sys", "importlib"]
                    if any(arg.lower() == module for module in restricted_modules):
                        raise SecurityError(
                            f"Potential security risk: '{arg}' is not allowed"
                        )
            return func(*args, **kwargs)

        return wrapper

    def _wrap_class(self, cls):
        class WrappedClass(cls, BaseRestrictedModule):
            def __getattribute__(self, name):
                # Avoid wrapping specific attributes like _wrap_function
                if name in {"_wrap_function", "__class__"}:
                    return super().__getattribute__(name)

                attr = super().__getattribute__(name)
                return self._wrap_function(attr) if callable(attr) else attr

        return WrappedClass


class SecurityError(Exception):
    pass
