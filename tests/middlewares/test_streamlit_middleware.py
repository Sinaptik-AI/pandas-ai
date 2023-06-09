"""Unit tests for the streamlit middleware class"""

from pandasai.middlewares.streamlit import StreamlitMiddleware


class TestStreamlitMiddleware:
    """Unit tests for the streamlit middleware class"""

    def test_streamlit_middleware(self):
        """Test the streamlit middleware"""
        code = "plt.show()"
        middleware = StreamlitMiddleware()
        assert middleware(code=code) == "st.pyplot()"
        assert middleware.has_run
