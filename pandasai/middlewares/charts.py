"""
Charts Middleware class

Middleware to handle the charts in PandasAI.
"""

from pandasai.middlewares.base import Middleware


class ChartsMiddleware(Middleware):
    """Charts Middleware class"""

    def run(self, code: str) -> str:
        """
        Run the middleware to remove issues with displaying charts in PandasAI.

        Returns:
            str: Modified code
        """

        if "plt.show()" in code and "plt.close('all')" not in code:
            code = code.replace("plt.show()", "plt.show()\nplt.close('all')")
        return code
