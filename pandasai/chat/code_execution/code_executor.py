import ast
from pandasai.chat.code_execution.environment import get_environment
from pandasai.exceptions import NoResultFoundError

from typing import Any, List


class CodeExecutor:
    """
    Handle the logic on how to handle different lines of code
    """

    _environment: dict

    def __init__(self, additional_dependencies: List[dict] = []) -> None:
        self._environment = get_environment(additional_dependencies)
        self._plots = []

    def add_to_env(self, key: str, value: Any) -> None:
        """
        Expose extra variables in the code to be used
        Args:
            key (str): Name of variable or lib alias
            value (Any): It can any value int, float, function, class etc.
        """
        self._environment[key] = value

    def execute(self, code: str) -> dict:
        exec(code, self._environment)
        return self._environment

    def execute_and_return_result(self, code: str) -> Any:
        """
        Executes the return updated environment
        """
        exec(code, self._environment)

        # Get the result
        if "result" not in self._environment:
            var_name, subscript = self._get_variable_last_line_of_code(code)
            if var_name and var_name in self._environment:
                if subscript is not None:
                    result = self._environment[var_name][subscript]
                else:
                    result = self._environment[var_name]

            raise NoResultFoundError("No result returned")
        else:
            result = self._environment["result"]

        if isinstance(result, dict) and result["type"] == "plot":
            for plot in self._plots:
                if plot["type"] == "plot":
                    result["value"] = plot["value"]

        return self._environment.get("result", None)

    def _get_variable_last_line_of_code(self, code: str) -> str:
        """
        Returns variable name from the last line if it is a variable name or assigned.
        Args:
            code (str): Code in string.

        Returns:
            str: Variable name.
        """
        try:
            tree = ast.parse(code)
            last_statement = tree.body[-1]

            if isinstance(last_statement, ast.Assign):
                return self._get_assign_variable(last_statement)
            elif isinstance(last_statement, ast.Expr):
                return self._get_expr_variable(last_statement)

            return ast.unparse(last_statement).strip()

        except SyntaxError:
            return None

    def _get_assign_variable(self, assign_node):
        """
        Extracts the variable name from an assignment node.

        Args:
            assign_node (ast.Assign): Assignment node.

        Returns:
            str: Variable name.
        """
        if isinstance(assign_node.targets[0], ast.Subscript):
            return self._get_subscript_variable(assign_node.targets[0])
        elif isinstance(assign_node.targets[0], ast.Name):
            return assign_node.targets[0].id, None

    def _get_expr_variable(self, expr_node):
        """
        Extracts the variable name from an expression node.

        Args:
            expr_node (ast.Expr): Expression node.

        Returns:
            str: Variable name.
        """
        if isinstance(expr_node.value, ast.Subscript):
            return self._get_subscript_variable(expr_node.value)
        elif isinstance(expr_node.value, ast.Name):
            return expr_node.value.id, None

    def _get_subscript_variable(self, subscript_node):
        """
        Extracts the variable name from a subscript node.

        Args:
            subscript_node (ast.Subscript): Subscript node.

        Returns:
            str: Variable name.
        """
        if isinstance(subscript_node.value, ast.Name):
            variable_name = subscript_node.value.id
            return variable_name, subscript_node.slice.value
