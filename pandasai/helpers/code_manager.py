import re
import ast
import uuid
from collections import defaultdict

import astor
import pandas as pd

from .node_visitors import AssignmentVisitor, CallVisitor
from .save_chart import add_save_chart
from .optional import import_dependency
from ..exceptions import BadImportError
from ..middlewares.base import Middleware
from ..constants import (
    WHITELISTED_BUILTINS,
    WHITELISTED_LIBRARIES,
)
from ..middlewares.charts import ChartsMiddleware
from typing import Union, List, Optional, Generator, Any
from ..helpers.logger import Logger
from ..schemas.df_config import Config
import logging
import traceback


class CodeManager:
    _dfs: List
    _middlewares: List[Middleware] = [ChartsMiddleware()]
    _config: Union[Config, dict]
    _logger: Logger = None
    _additional_dependencies: List[dict] = []
    _ast_comparatos_map: dict = {
        ast.Eq: "=",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Is: "is",
        ast.IsNot: "is not",
        ast.In: "in",
        ast.NotIn: "not in",
    }
    _current_code_executed: str = None
    _last_code_executed: str = None

    def __init__(
        self,
        dfs: List,
        config: Union[Config, dict],
        logger: Logger,
    ):
        """
        Args:
            config (Union[Config, dict], optional): Config to be used. Defaults to None.
            logger (Logger, optional): Logger to be used. Defaults to None.
        """

        self._dfs = dfs
        self._config = config
        self._logger = logger

        if self._config.middlewares is not None:
            self.add_middlewares(*self._config.middlewares)

    def add_middlewares(self, *middlewares: Optional[Middleware]):
        """
        Add middlewares to PandasAI instance.

        Args:
            *middlewares: Middlewares to be added

        """
        self._middlewares.extend(middlewares)

    def _execute_catching_errors(
        self, code: str, environment: dict
    ) -> Optional[Exception]:
        """
        Perform execution of the code directly.
        Call `exec()` for the given `code`, catch any non-base exceptions.

        Args:
            code (str): Python code.
            environment (dict): Context for the `exec()`.

        Returns:
            (Optional[Exception]): Any exception raised during execution.
                `None` if executed without exceptions.
        """
        try:
            # Check in the code that analyze_data function is called.
            # If not, add it.
            if " = analyze_data(" not in code:
                code += "\n\nresult = analyze_data(dfs)"

            exec(code, environment)
        except Exception as exc:
            self._logger.log("Error of executing code", level=logging.WARNING)
            self._logger.log(f"{traceback.format_exc()}", level=logging.DEBUG)

            return exc

    def _handle_error(
        self,
        exc: Exception,
        code: str,
        environment: dict,
        use_error_correction_framework: bool = True,
    ):
        """
        Handle error occurred during first executing of code.
        If `exc` is instance of `NameError`, try to import the name, extend
        the context and then call `_execute_catching_errors()` again.
        If OK, returns the code string; if failed, continuing handling.
        Args:
            exc (Exception): The caught exception.
            code (str): Python code.
            environment (dict): Context for the `exec()`
        Raises:
            Exception: Any exception which has been caught during
                the very first execution of the code.
        Returns:
            str: Python code. Either original or new one, given by
                error correction framework.
        """
        if isinstance(exc, NameError):
            name_to_be_imported = None
            if hasattr(exc, "name"):
                name_to_be_imported = exc.name
            elif exc.args and isinstance(exc.args[0], str):
                name_ptrn = r"'([0-9a-zA-Z_]+)'"
                if search_name_res := re.search(name_ptrn, exc.args[0]):
                    name_to_be_imported = search_name_res.group(1)

            if name_to_be_imported and name_to_be_imported in WHITELISTED_LIBRARIES:
                try:
                    package = import_dependency(name_to_be_imported)
                    environment[name_to_be_imported] = package

                    caught_error = self._execute_catching_errors(code, environment)
                    if caught_error is None:
                        return code

                except ModuleNotFoundError:
                    self._logger.log(
                        f"Unable to fix `NameError`: package '{name_to_be_imported}'"
                        f" could not be imported.",
                        level=logging.DEBUG,
                    )
                except Exception as new_exc:
                    exc = new_exc
                    self._logger.log(
                        f"Unable to fix `NameError`: an exception was raised: "
                        f"{traceback.format_exc()}",
                        level=logging.DEBUG,
                    )

            if not use_error_correction_framework:
                raise exc

    def _required_dfs(self, code: str) -> List[str]:
        """
        List the index of the DataFrames that are needed to execute the code. The goal
        is to avoid to run the connectors if the code does not need them.

        Args:
            code (str): Python code to execute

        Returns:
            List[int]: A list of the index of the DataFrames that are needed to execute
            the code.
        """

        required_dfs = []
        for i, df in enumerate(self._dfs):
            if f"dfs[{i}]" in code:
                required_dfs.append(df)
            else:
                required_dfs.append(None)
        return required_dfs

    def execute_code(
        self,
        code: str,
        prompt_id: uuid.UUID,
    ) -> Any:
        """
        Execute the python code generated by LLMs to answer the question
        about the input dataframe. Run the code in the current context and return the
        result.

        Args:
            code (str): Python code to execute.
            prompt_id (uuid.UUID): UUID of the request.

        Returns:
            Any: The result of the code execution. The type of the result depends
                on the generated code.

        """
        self._current_code_executed = code

        for middleware in self._middlewares:
            code = middleware(code)

        # Add save chart code
        if self._config.save_charts:
            code = add_save_chart(
                code,
                logger=self._logger,
                file_name=str(prompt_id),
                save_charts_path=self._config.save_charts_path,
            )

        # Get the code to run removing unsafe imports and df overwrites
        code_to_run = self._clean_code(code)
        self.last_code_executed = code_to_run
        self._logger.log(
            f"""
Code running:
```
{code_to_run}
        ```"""
        )

        # List the required dfs, so we can avoid to run the connectors
        # if the code does not need them
        dfs = self._required_dfs(code_to_run)
        environment: dict = self._get_environment()
        environment["dfs"] = self._get_samples(dfs)

        caught_error = self._execute_catching_errors(code_to_run, environment)
        if caught_error is not None:
            self._handle_error(
                caught_error,
                code_to_run,
                environment,
                use_error_correction_framework=self._config.use_error_correction_framework,
            )

        analyze_data = environment.get("analyze_data", None)

        return analyze_data(self._get_originals(dfs))

    def _get_samples(self, dfs):
        """
        Get samples from the dfs

        Args:
            dfs (list): List of dfs

        Returns:
            list: List of samples
        """
        samples = []
        for df in dfs:
            if df is not None:
                samples.append(df.head_df)
            else:
                samples.append(None)
        return samples

    def _get_originals(self, dfs):
        """
        Get original dfs

        Args:
            dfs (list): List of dfs

        Returns:
            list: List of dfs
        """
        original_dfs = []
        for index, df in enumerate(dfs):
            if df is None:
                original_dfs.append(None)
                continue

            if df.has_connector:
                extracted_filters = self._extract_filters(self._current_code_executed)
                filters = extracted_filters.get(f"dfs[{index}]", [])
                df.connector.set_additional_filters(filters)
                df.load_connector(temporary=len(filters) > 0)

            original_dfs.append(df.dataframe)

        return original_dfs

    def _get_environment(self) -> dict:
        """
        Returns the environment for the code to be executed.

        Returns (dict): A dictionary of environment variables
        """

        return {
            "pd": pd,
            **{
                lib["alias"]: getattr(import_dependency(lib["module"]), lib["name"])
                if hasattr(import_dependency(lib["module"]), lib["name"])
                else import_dependency(lib["module"])
                for lib in self._additional_dependencies
            },
            "__builtins__": {
                **{builtin: __builtins__[builtin] for builtin in WHITELISTED_BUILTINS},
                "__build_class__": __build_class__,
                "__name__": "__main__",
            },
        }

    def _is_jailbreak(self, node: ast.stmt) -> bool:
        """
        Remove jailbreaks from the code to prevent malicious code execution.
        Args:
            node (ast.stmt): A code node to be checked.
        Returns (bool):
        """

        DANGEROUS_BUILTINS = ["__subclasses__", "__builtins__", "__import__"]

        node_str = ast.dump(node)

        for builtin in DANGEROUS_BUILTINS:
            if builtin in node_str:
                return True

        return False

    def _is_unsafe(self, node: ast.stmt) -> bool:
        """
        Remove unsafe code from the code to prevent malicious code execution.

        Args:
            node (ast.stmt): A code node to be checked.

        Returns (bool):
        """

        code = astor.to_source(node)
        if any(
            method in code
            for method in [
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
        ):
            return True

        return False

    def _sanitize_analyze_data(self, analyze_data_node: ast.stmt) -> ast.stmt:
        # Sanitize the code within analyze_data
        sanitized_analyze_data = []
        for node in analyze_data_node.body:
            if (
                self._is_df_overwrite(node)
                or self._is_jailbreak(node)
                or self._is_unsafe(node)
            ):
                continue
            sanitized_analyze_data.append(node)

        analyze_data_node.body = sanitized_analyze_data
        return analyze_data_node

    def _clean_code(self, code: str) -> str:
        """
        A method to clean the code to prevent malicious code execution.

        Args:
            code(str): A python code.

        Returns:
            str: A clean code string.

        """

        # Clear recent optional dependencies
        self._additional_dependencies = []

        tree = ast.parse(code)

        # Check for imports and the node where analyze_data is defined
        new_body = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._check_imports(node)
                continue
            if isinstance(node, ast.FunctionDef) and node.name == "analyze_data":
                analyze_data_node = node
                sanitized_analyze_data = self._sanitize_analyze_data(analyze_data_node)
                new_body.append(sanitized_analyze_data)
                continue
            new_body.append(node)

        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree, pretty_source=lambda x: "".join(x)).strip()

    def _is_df_overwrite(self, node: ast.stmt) -> bool:
        """
        Remove df declarations from the code to prevent malicious code execution.

        Args:
            node (ast.stmt): A code node to be checked.

        Returns (bool):

        """

        return (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "dfs"
        )

    def _check_imports(self, node: Union[ast.Import, ast.ImportFrom]):
        """
        Add whitelisted imports to _additional_dependencies.

        Args:
            node (object): ast.Import or ast.ImportFrom

        Raises:
            BadImportError: If the import is not whitelisted

        """
        if isinstance(node, ast.Import):
            module = node.names[0].name
        else:
            module = node.module

        library = module.split(".")[0]

        if library == "pandas":
            return

        if (
            library
            in WHITELISTED_LIBRARIES + self._config.custom_whitelisted_dependencies
        ):
            for alias in node.names:
                self._additional_dependencies.append(
                    {
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname or alias.name,
                    }
                )
            return

        if library not in WHITELISTED_BUILTINS:
            raise BadImportError(library)

    @staticmethod
    def _get_nearest_func_call(
        current_lineno: int, calls: list[ast.Call], func_name: str
    ) -> ast.Call:
        """
        Utility function to get the nearest previous call node.

        Sort call nodes list (copy of the list) by line number.
        Iterate over the call nodes list. If the call node's function name
        equals to `func_name`, set `nearest_call` to the node object.

        Args:
            current_lineno (int): Number of the current processed line.
            calls (list[ast.Assign]): List of call nodes.
            func_name (str): Name of the target function.

        Returns:
            ast.Call: The node of the nearest previous call `<func_name>()`.
        """
        calls = sorted(calls, key=lambda node: node.lineno)
        nearest_call = None
        for call_node in calls:
            if call_node.lineno > current_lineno:
                return nearest_call
            try:
                if call_node.func.attr == func_name:
                    nearest_call = call_node
            except AttributeError:
                continue

    @staticmethod
    def _tokenize_operand(operand_node: ast.expr) -> Generator[str, None, None]:
        """
        Utility generator function to get subscript slice contants.

        Args:
            operand_node (ast.expr):
                The node to be tokenized.
        Yields:
            str: Token string.

        Examples:
            >>> code = '''
            ... foo = [1, [2, 3], [[4, 5], [6, 7]]]
            ... print(foo[2][1][0])
            ... '''
            >>> tree = ast.parse(code)
            >>> res = CodeManager._tokenize_operand(tree.body[1].value.args[0])
            >>> print(list(res))
            ['foo', 2, 1, 0]
        """
        if isinstance(operand_node, ast.Subscript):
            slice_ = operand_node.slice.value
            yield from CodeManager._tokenize_operand(operand_node.value)
            yield slice_

        if isinstance(operand_node, ast.Name):
            yield operand_node.id

        if isinstance(operand_node, ast.Constant):
            yield operand_node.value

    @staticmethod
    def _get_df_id_by_nearest_assignment(
        current_lineno: int, assignments: list[ast.Assign], target_name: str
    ):
        """
        Utility function to get df label by finding the nearest assigment.

        Sort assignment nodes list (copy of the list) by line number.
        Iterate over the assignment nodes list. If the assignment node's value
        looks like `dfs[<index>]` and target label equals to `target_name`,
        set `nearest_assignment` to "dfs[<index>]".

        Args:
            current_lineno (int): Number of the current processed line.
            assignments (list[ast.Assign]): List of assignment nodes.
            target_name (str): Name of the target variable. The assignment
                node is supposed to assign to this name.

        Returns:
            str: The string representing df label, looks like "dfs[<index>]".
        """
        nearest_assignment = None
        assignments = sorted(assignments, key=lambda node: node.lineno)
        for assignment in assignments:
            if assignment.lineno > current_lineno:
                return nearest_assignment
            try:
                is_subscript = isinstance(assignment.value, ast.Subscript)
                dfs_on_the_right = assignment.value.value.id == "dfs"
                assign_to_target = assignment.targets[0].id == target_name
                if is_subscript and dfs_on_the_right and assign_to_target:
                    nearest_assignment = f"dfs[{assignment.value.slice.value}]"
            except AttributeError:
                continue

    def _extract_comparisons(self, tree: ast.Module) -> dict[str, list]:
        """
        Process nodes from passed tree to extract filters.

        Collects all assignments in the tree.
        Collects all function calls in the tree.
        Walk over the tree and handle each comparison node.
        For each comparison node, defined what `df` is this node related to.
        Parse constants values from the comparison node.
        Add to the result dict.

        Args:
            tree (str): A snippet of code to be parsed.

        Returns:
            dict: The `defaultdict(list)` instance containing all filters
                parsed from the passed instructions tree. The dictionary has
                the following structure:
                {
                    "<df_number>": [
                        ("<left_operand>", "<operator>", "<right_operand>")
                    ]
                }
        """
        comparisons = defaultdict(list)
        current_df = "dfs[0]"

        visitor = AssignmentVisitor()
        visitor.visit(tree)
        assignments = visitor.assignment_nodes

        call_visitor = CallVisitor()
        call_visitor.visit(tree)
        calls = call_visitor.call_nodes

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                is_call_on_left = isinstance(node.left, ast.Call)
                is_polars = False
                is_calling_col = False
                try:
                    is_polars = node.left.func.value.id in ("pl", "polars")
                    is_calling_col = node.left.func.attr == "col"
                except AttributeError:
                    pass

                if is_call_on_left and is_polars and is_calling_col:
                    df_name = self._get_nearest_func_call(
                        node.lineno, calls, "filter"
                    ).func.value.id
                    current_df = self._get_df_id_by_nearest_assignment(
                        node.lineno, assignments, df_name
                    )
                    left_str = node.left.args[0].value

                    for op, right in zip(node.ops, node.comparators):
                        op_str = self._ast_comparatos_map.get(type(op), "Unknown")
                        right_str = right.value

                        comparisons[current_df].append((left_str, op_str, right_str))
                elif isinstance(node.left, ast.Subscript):
                    name, *slices = self._tokenize_operand(node.left)
                    current_df = (
                        self._get_df_id_by_nearest_assignment(
                            node.lineno, assignments, name
                        )
                        or current_df
                    )
                    left_str = name if not slices else slices[-1]

                    for op, right in zip(node.ops, node.comparators):
                        op_str = self._ast_comparatos_map.get(type(op), "Unknown")
                        name, *slices = self._tokenize_operand(right)
                        right_str = name if not slices else slices[-1]

                        comparisons[current_df].append((left_str, op_str, right_str))
        return comparisons

    def _extract_filters(self, code) -> dict[str, list]:
        """
        Extract filters to be applied to the dataframe from passed code.

        Args:
            code (str): A snippet of code to be parsed.

        Returns:
            dict: The dictionary containing all filters parsed from
                the passed code. The dictionary has the following structure:
                {
                    "<df_number>": [
                        ("<left_operand>", "<operator>", "<right_operand>")
                    ]
                }

        Raises:
            SyntaxError: If the code is unable to be parsed by `ast.parse()`.
            Exception: If any exception is raised during working with nodes
                of the code tree.
        """
        try:
            parsed_tree = ast.parse(code)
        except SyntaxError:
            self._logger.log(
                "Invalid code passed for extracting filters", level=logging.ERROR
            )
            self._logger.log(f"{traceback.format_exc()}", level=logging.DEBUG)
            raise

        try:
            filters = self._extract_comparisons(parsed_tree)
        except Exception:
            self._logger.log(
                "Unable to extract filters for passed code", level=logging.ERROR
            )
            self._logger.log(f"{traceback.format_exc()}", level=logging.DEBUG)
            raise

        return filters

    @property
    def middlewares(self):
        return self._middlewares

    @property
    def last_code_executed(self):
        return self._last_code_executed

    @last_code_executed.setter
    def last_code_executed(self, code: str):
        self._last_code_executed = code
