"""Module to import optional dependencies.

Source: Taken from pandas/compat/_optional.py
"""

import importlib
import types

INSTALL_MAPPING = {}


def get_version(module: types.ModuleType) -> str:
    """Get the version of a module."""
    version = getattr(module, "__version__", None)

    if version is None:
        raise ImportError(f"Can't determine version for {module.__name__}")

    return version


_DANGEROUS_MODULES = frozenset(
    {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "pathlib",
        "io",
        "ctypes",
        "signal",
        "multiprocessing",
        "threading",
        "pickle",
        "marshal",
        "shelve",
        "dbm",
        "sqlite3",
        "importlib",
        "code",
        "codeop",
        "compileall",
        "py_compile",
        "zipimport",
        "pkgutil",
        "pdb",
        "profile",
        "cProfile",
        "timeit",
        "trace",
        "tracemalloc",
        "faulthandler",
        "platform",
        "webbrowser",
        "cgi",
        "cgitb",
        "xmlrpc",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "telnetlib",
        "uuid",
        "ssl",
        "hashlib",
        "hmac",
        "secrets",
        "textwrap",
        "difflib",
        "unicodedata",
        "stringprep",
        "readline",
        "rlcompleter",
        "struct",
        "codecs",
        "encodings",
        "tokenize",
        "keyword",
        "token",
        "tabnanny",
        "pyclbr",
        "pydoc",
        "doctest",
        "unittest",
        "test",
        "distutils",
        "ensurepip",
        "venv",
        "zipapp",
        "builtins",
        "_thread",
        "weakref",
        "types",
        "copyreg",
    }
)


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Safe wrapper around __import__ that blocks imports of dangerous modules.

    This provides runtime defense-in-depth: even if the AST-level validation
    in CodeRequirementValidator is bypassed, dangerous module imports will be
    blocked at execution time.

    Matches the standard __import__ signature so it works as a drop-in replacement.
    """
    module_root = name.split(".")[0]
    if module_root in _DANGEROUS_MODULES:
        raise ImportError(
            f"Import of module '{name}' is not allowed in LLM-generated code. "
            f"Imports of system/OS-level modules are blocked for security."
        )
    return importlib.__import__(name, globals, locals, fromlist, level)


def _get_restricted_builtins() -> dict:
    """
    Returns a restricted subset of Python builtins safe for LLM-generated code.

    Provides a safe __import__ wrapper that blocks dangerous modules while
    allowing legitimate imports (pandas, numpy, matplotlib, etc.).

    Excludes dangerous builtins such as open, exec, eval, compile, getattr,
    setattr, delattr, globals, locals, vars, dir, breakpoint, exit, quit,
    help, input, memoryview, super, staticmethod, classmethod, property,
    bytearray, bytes, frozenset, hash, id, callable, next.

    Returns:
        dict: A dictionary of safe builtins.
    """
    import builtins as _builtins

    _SAFE_NAMES = {
        "True",
        "False",
        "None",
        "bool",
        "int",
        "float",
        "str",
        "list",
        "dict",
        "tuple",
        "set",
        "type",
        "isinstance",
        "issubclass",
        "len",
        "range",
        "enumerate",
        "zip",
        "map",
        "filter",
        "sorted",
        "reversed",
        "min",
        "max",
        "sum",
        "abs",
        "round",
        "pow",
        "divmod",
        "print",
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "AttributeError",
        "NameError",
        "ZeroDivisionError",
        "RuntimeError",
        "StopIteration",
        "NotImplementedError",
        "ArithmeticError",
        "OverflowError",
        "FloatingPointError",
        "LookupError",
        "AssertionError",
        "OSError",
        "IOError",
        "FileNotFoundError",
        "ConnectionError",
        "TimeoutError",
        "SyntaxError",
        "IndentationError",
        "TabError",
        "MemoryError",
        "RecursionError",
        "UnicodeError",
        "BytesWarning",
        "DeprecationWarning",
        "FutureWarning",
        "UserWarning",
        "RuntimeWarning",
        "PendingDeprecationWarning",
        "ImportWarning",
        "UnicodeWarning",
        "ResourceWarning",
    }

    builtins_dict = {
        name: getattr(_builtins, name)
        for name in _SAFE_NAMES
        if hasattr(_builtins, name)
    }

    builtins_dict["__import__"] = _safe_import

    return builtins_dict


def get_environment() -> dict:
    """
    Returns the environment for the code to be executed.

    The environment includes a restricted set of Python builtins to prevent
    LLM-generated code from performing dangerous operations such as importing
    arbitrary modules, accessing the filesystem, or executing system commands.

    Returns (dict): A dictionary of environment variables
    """
    env = {
        "pd": import_dependency("pandas"),
        "plt": import_dependency("matplotlib.pyplot"),
        "np": import_dependency("numpy"),
        "__builtins__": _get_restricted_builtins(),
    }

    return env


def import_dependency(
    name: str,
    extra: str = "",
    errors: str = "raise",
):
    """
    Import an optional dependency.

    By default, if a dependency is missing an ImportError with a nice
    message will be raised. If a dependency is present, but too old,
    we raise.

    Args:
        name (str): The module name.
        extra (str): An additional text to include in the ImportError message.
        errors (str): Representing an action to do when a dependency
            is not found or its version is too old.
            Possible values: "raise", "warn", "ignore":
                * raise : Raise an ImportError
                * warn : Only applicable when a module's version is too old.
                  Warns that the version is too old and returns None
                * ignore: If the module is not installed, return None, otherwise,
                  return the module, even if the version is too old.
                  It's expected that users validate the version locally when
                  using ``errors="ignore"`` (see. ``io/html.py``)
        min_version (str): Specify a minimum version that is different from
            the global pandas minimum version required. Defaults to None.

    Returns:
         Optional[module]:
            The imported module, when found and the version is correct.
            None is returned when the package is not found and `errors`
            is False, or when the package's version is too old and `errors`
            is `'warn'`.
    """

    assert errors in {"warn", "raise", "ignore"}

    package_name = INSTALL_MAPPING.get(name)
    install_name = package_name if package_name is not None else name

    msg = (
        f"Missing optional dependency '{install_name}'. {extra} "
        f"Use pip or conda to install {install_name}."
    )
    try:
        module = importlib.import_module(name)
    except ImportError as exc:
        if errors == "raise":
            raise ImportError(msg) from exc
        return None

    return module
