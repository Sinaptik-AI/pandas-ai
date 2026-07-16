import ast

from pandasai.agent.state import AgentState
from pandasai.exceptions import ExecuteSQLQueryNotUsed, MaliciousCodeGenerated

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


class CodeRequirementValidator:
    """
    Class to validate code requirements based on a pipeline context.
    """

    class _FunctionCallVisitor(ast.NodeVisitor):
        """
        AST visitor to collect all function calls in a given Python code.
        """

        def __init__(self):
            self.function_calls = []

        def visit_Call(self, node: ast.Call):
            """
            Visits a function call and records its name or attribute.
            """
            if isinstance(node.func, ast.Name):
                self.function_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and isinstance(
                node.func.value, ast.Name
            ):
                self.function_calls.append(f"{node.func.value.id}.{node.func.attr}")
            self.generic_visit(node)  # Continue visiting child nodes

    class _SecurityVisitor(ast.NodeVisitor):
        """
        AST visitor to detect dangerous code patterns that could enable
        arbitrary code execution, file system access, or system command execution.

        Blocks:
        - import / from ... import statements for dangerous modules
        - __import__() calls
        - Access to dangerous module attributes (e.g., os.system, subprocess.Popen)
        """

        def visit_Import(self, node: ast.Import):
            for alias in node.names:
                module_root = alias.name.split(".")[0]
                if module_root in _DANGEROUS_MODULES:
                    raise MaliciousCodeGenerated(
                        f"Generated code contains import of dangerous module: '{alias.name}'. "
                        f"Imports of system/OS-level modules are not allowed."
                    )
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom):
            if node.module:
                module_root = node.module.split(".")[0]
                if module_root in _DANGEROUS_MODULES:
                    raise MaliciousCodeGenerated(
                        f"Generated code imports from dangerous module: '{node.module}'. "
                        f"Imports of system/OS-level modules are not allowed."
                    )
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call):
            # Block __import__() calls
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                raise MaliciousCodeGenerated(
                    "Generated code contains __import__() call, which is not allowed."
                )
            # Block builtins.__import__() calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "__import__":
                raise MaliciousCodeGenerated(
                    "Generated code contains builtins.__import__() call, which is not allowed."
                )
            self.generic_visit(node)

        def visit_Attribute(self, node: ast.Attribute):
            # Walk up the attribute chain to find the root name
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name) and root.id in _DANGEROUS_MODULES:
                raise MaliciousCodeGenerated(
                    f"Generated code accesses dangerous module '{root.id}' "
                    f"via attribute '{node.attr}'. "
                    f"Access to system/OS-level modules is not allowed."
                )
            self.generic_visit(node)

    def __init__(self, context: AgentState):
        """
        Initialize the validator with the pipeline context.

        Args:
            context (AgentState): The agent state containing the configuration.
        """
        self.context = context

    def validate(self, code: str) -> bool:
        """
        Validates whether the code meets the requirements specified by the pipeline context.

        Args:
            code (str): The code to validate.

        Returns:
            bool: True if the code meets the requirements, False otherwise.

        Raises:
            MaliciousCodeGenerated: If the code contains dangerous patterns
                (imports of system modules, __import__ calls, etc.).
            ExecuteSQLQueryNotUsed: If `execute_sql_query` is not used in the code.
        """
        tree = ast.parse(code)

        # Security check: detect dangerous code patterns
        security_visitor = self._SecurityVisitor()
        security_visitor.visit(tree)

        # Use the visitor to collect function calls
        func_call_visitor = self._FunctionCallVisitor()
        func_call_visitor.visit(tree)

        # Validate requirements
        if "execute_sql_query" not in func_call_visitor.function_calls:
            raise ExecuteSQLQueryNotUsed(
                "The code must execute SQL queries using the `execute_sql_query` function, which is already defined!"
            )

        return True
