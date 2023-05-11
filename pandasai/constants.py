"""
Constants used in the pandasai package.
"""

# Code block tags
START_CODE_TAG = "<start_code>"
END_CODE_TAG = "<end_code>"

# Whitelisted libraries and built-in functions
WHITELISTED_LIBRARIES = ("numpy", "matplotlib")
WHITELISTED_BUILTINS = (
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
    "callable", "chr", "classmethod", "complex", "delattr", "dict", "dir",
    "divmod", "enumerate", "filter", "float", "format", "frozenset", "getattr",
    "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
    "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
    "min", "next", "object", "oct", "open", "ord", "pow", "print", "property",
    "range", "repr", "reversed", "round", "set", "setattr", "slice", "sorted",
    "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip"
)
