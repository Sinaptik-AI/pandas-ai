import ast

from pandasai.agent.state import AgentState
from pandasai.exceptions import ExecuteSQLQueryNotUsed


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
            ExecuteSQLQueryNotUsed: If `execute_sql_query` is not used in the code.
        """
        # Parse the code into an AST
        tree = ast.parse(code)

        # Use the visitor to collect function calls
        func_call_visitor = self._FunctionCallVisitor()
        func_call_visitor.visit(tree)

        # Validate requirements
        if "execute_sql_query" not in func_call_visitor.function_calls:
            raise ExecuteSQLQueryNotUsed(
                "The code must execute SQL queries using the `execute_sql_query` function, which is already defined!"
            )

        return True
