class BaseRestrictedModule:
    def _wrap_function(self, func):
        def wrapper(*args, **kwargs):
            # Check for any suspicious arguments that might be used for importing
            for arg in args + tuple(kwargs.values()):
                if isinstance(arg, str) and any(
                    module == arg.lower()
                    for module in ["io", "os", "subprocess", "sys", "importlib"]
                ):
                    raise SecurityError(
                        f"Potential security risk: '{arg}' is not allowed"
                    )
            return func(*args, **kwargs)

        return wrapper

    def _wrap_class(self, cls):
        class WrappedClass(cls):
            def __getattribute__(self, name):
                attr = super().__getattribute__(name)
                return self._wrap_function(self, attr) if callable(attr) else attr

        return WrappedClass


class SecurityError(Exception):
    pass
