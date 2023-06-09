"""
Constants used in the pandasai package.

It includes Start & End Code tags, Whitelisted Python Packages and
While List Builtin Methods.

"""

START_CODE_TAG = "<startCode>"
END_CODE_TAG = "<endCode>"

# List of Python packages that are whitelisted for import in generated code
#   and are installed by default.
WHITELISTED_LIBRARIES = [
    "numpy",
]

# List of Python packages that are added to the environment by default.
ENVIRONMENT_DEFAULTS = {
    "pandas": "pd",
    "matplotlib.pyplot": "plt",
}

# List of Python builtin libraries that are added to the environment by default.
WHITELISTED_BUILTINS = [
    "abs",
    "all",
    "any",
    "ascii",
    "bin",
    "bool",
    "bytearray",
    "bytes",
    "callable",
    "chr",
    "classmethod",
    "complex",
    "delattr",
    "dict",
    "dir",
    "divmod",
    "enumerate",
    "filter",
    "float",
    "format",
    "frozenset",
    "getattr",
    "hasattr",
    "hash",
    "help",
    "hex",
    "id",
    "input",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "locals",
    "map",
    "max",
    "memoryview",
    "min",
    "next",
    "object",
    "oct",
    "open",
    "ord",
    "pow",
    "print",
    "property",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "setattr",
    "slice",
    "sorted",
    "staticmethod",
    "str",
    "sum",
    "super",
    "tuple",
    "type",
    "vars",
    "zip",
]

# List of Python packages that are whitelisted for import in generated code
#   but are not installed by default.
WHITELISTED_OPTIONAL_LIBRARIES = [
    "sklearn",
    "statsmodels",
    "seaborn",
    "plotly",
    "ggplot",
]
