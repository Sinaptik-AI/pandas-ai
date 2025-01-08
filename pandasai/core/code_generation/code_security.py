import ast
import re

import astor

from pandasai.agent.state import AgentState
from pandasai.constants import RESTRICTED_LIBS
from pandasai.exceptions import MaliciousCodeGenerated


class CodeSecurityChecker:
    """
    A class to perform checks for malicious and unsafe code execution.
    """

    def __init__(self, context: AgentState):
        """
        Initialize the CodeSecurityChecker with the provided context.

        Args:
            context (AgentState): The pipeline context for the code checks.
        """
        self.context = context
        self.dangerous_modules = [
            " os",
            " io",
            ".os",
            ".io",
            "'os'",
            "'io'",
            '"os"',
            '"io"',
            "chr(",
            "chr)",
            "chr ",
            "(chr",
            "b64decode",
        ]
        self.dangerous_builtins = ["__subclasses__", "__builtins__", "__import__"]
        self.unsafe_methods = [
            ".to_csv",
            ".to_excel",
            ".to_json",
            ".to_sql",
            ".to_feather",
            ".to_hdf",
            ".to_parquet",
            ".to_pickle",
            ".to_gbq",
            ".to_stata",
            ".to_records",
            ".to_latex",
            ".to_html",
            ".to_markdown",
            ".to_clipboard",
        ]

    def _is_malicious_code(self, code: str) -> bool:
        """
        Check if the provided code contains malicious content.

        Args:
            code (str): The code to be checked.

        Returns:
            bool: True if malicious code is found, otherwise False.
        """
        tree = ast.parse(code)

        def check_restricted_access(node):
            """Check if the node accesses restricted modules or private attributes."""
            if isinstance(node, ast.Attribute):
                attr_chain = []
                while isinstance(node, ast.Attribute):
                    if node.attr.startswith("_"):
                        raise MaliciousCodeGenerated(
                            f"Access to private attribute '{node.attr}' is not allowed."
                        )
                    attr_chain.insert(0, node.attr)
                    node = node.value
                if isinstance(node, ast.Name):
                    attr_chain.insert(0, node.id)
                    if any(module in RESTRICTED_LIBS for module in attr_chain):
                        raise MaliciousCodeGenerated(
                            f"Restricted access detected in attribute chain: {'.'.join(attr_chain)}"
                        )
            elif isinstance(node, ast.Subscript) and isinstance(
                node.value, ast.Attribute
            ):
                check_restricted_access(node.value)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    sub_module_names = alias.name.split(".")
                    if any(module in RESTRICTED_LIBS for module in sub_module_names):
                        raise MaliciousCodeGenerated(
                            f"Restricted library import detected: {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                sub_module_names = node.module.split(".")
                if any(module in RESTRICTED_LIBS for module in sub_module_names):
                    raise MaliciousCodeGenerated(
                        f"Restricted library import detected: {node.module}"
                    )
                if any(alias.name in RESTRICTED_LIBS for alias in node.names):
                    raise MaliciousCodeGenerated(
                        "Restricted library import detected in 'from ... import ...'"
                    )
            elif isinstance(node, (ast.Attribute, ast.Subscript)):
                check_restricted_access(node)

        return any(
            re.search(r"\b" + re.escape(module) + r"\b", code)
            for module in self.dangerous_modules
        )

    def _is_jailbreak(self, node: ast.stmt) -> bool:
        """
        Check if the code node contains jailbreak methods.

        Args:
            node (ast.stmt): A code node to be checked.

        Returns:
            bool: True if jailbreak methods are found, otherwise False.
        """
        node_str = ast.dump(node)
        return any(builtin in node_str for builtin in self.dangerous_builtins)

    def _is_unsafe(self, node: ast.stmt) -> bool:
        """
        Check if the code node contains unsafe operations.

        Args:
            node (ast.stmt): A code node to be checked.

        Returns:
            bool: True if unsafe operations are found, otherwise False.
        """
        code = astor.to_source(node)
        return any(method in code for method in self.unsafe_methods)

    def check(self, code: str) -> None:
        """
        Perform all checks on the provided code.

        Args:
            code (str): The code to be checked.

        Raises:
            MaliciousCodeGenerated: If malicious or unsafe code is detected.
        """
        if self._is_malicious_code(code):
            raise MaliciousCodeGenerated("Malicious code is generated!")

        tree = ast.parse(code)
        for node in tree.body:
            if self._is_jailbreak(node):
                raise MaliciousCodeGenerated("Restricted builtins are used!")
            if self._is_unsafe(node):
                raise MaliciousCodeGenerated(
                    "The code is unsafe and can lead to I/O operations or other malicious operations that are not permitted!"
                )
