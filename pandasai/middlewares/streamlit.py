"""
Streamlit Middleware class

Middleware to run the code in streamlit and address the issues with streamlit
integration with PandasAI.
"""

from pandasai.middlewares.base import Middleware


class StreamlitMiddleware(Middleware):
    """Streamlit Middleware class"""

    def run(self, code: str) -> str:
        """
        Run the middleware to make the code compatible with streamlit.
        For example, it replaces `plt.show()` with `st.pyplot()`.

        Returns:
            str: Modified code
        """

        code = code.replace("plt.show()", "st.pyplot(plt.gcf())")
        code = "import streamlit as st\n" + code
        return code
