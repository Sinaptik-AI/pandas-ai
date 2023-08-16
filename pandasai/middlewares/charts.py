"""
Charts Middleware class

Middleware to handle the charts in PandasAI.
"""

from pandasai.middlewares.base import Middleware
import sys
import ast


class ChartsMiddleware(Middleware):
    """Charts Middleware class"""

    def _is_running_in_console(self) -> bool:
        """
        Check if the code is running in console or not.

        Returns:
            bool: True if running in console else False
        """

        return sys.stdout.isatty()

    def run(self, code: str) -> str:
        """
        Run the middleware to remove issues with displaying charts in PandasAI.

        Returns:
            str: Modified code
        """

        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute) and call.func.attr == "show":
                    if "plt.close('all')" not in code:
                        code = code.replace(
                            "plt.show()", "plt.show()\nplt.close('all')"
                        )

                    if not self._is_running_in_console():
                        code = code.replace("plt.show()", "plt.show(block=False)")
                    break
        return code
