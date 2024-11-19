"""
Constants used in the pandasai package.

It includes Start & End Code tags, Whitelisted Python Packages and
While List Builtin Methods.

"""

# Default directory to store chart if user doesn't provide any
DEFAULT_CHART_DIRECTORY = "exports/charts"

# Default directory for cache
DEFAULT_CACHE_DIRECTORY = "cache"

# Default permissions for files and directories
DEFAULT_FILE_PERMISSIONS = 0o755

# Token needed to invalidate the cache after breaking changes
CACHE_TOKEN = "pandasai1"

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
WHITELISTED_LIBRARIES = [
    "seaborn",
    "matplotlib",
    "numpy",
    "datetime",
    "json",
    "base64",
    "pandas",
]

# List of restricted libs
RESTRICTED_LIBS = [
    "os",  # OS-level operations (file handling, environment variables)
    "sys",  # System-level access
    "subprocess",  # Run system commands
    "shutil",  # File operations, including delete
    "multiprocessing",  # Spawn new processes
    "threading",  # Thread-level operations
    "socket",  # Network connections
    "http",  # HTTP requests
    "ftplib",  # FTP connections
    "paramiko",  # SSH operations
    "tempfile",  # Create temporary files
    "pathlib",  # Filesystem path handling
    "resource",  # Access resource usage limits (system-related)
    "ssl",  # SSL socket connections
    "pickle",  # Unsafe object serialization
    "ctypes",  # C-level interaction with memory
    "psutil",  # System and process utilities
    "io",
]

PANDASBI_SETUP_MESSAGE = (
    "The api_key client option must be set either by passing api_key to the client "
    "or by setting the PANDASAI_API_KEY environment variable. To get the key follow below steps:\n"
    "1. Go to https://www.pandabi.ai and sign up\n"
    "2. From settings go to API keys and copy\n"
    "3. Set environment variable like os.environ['PANDASAI_API_KEY'] = '$2a$10$flb7....'"
)
