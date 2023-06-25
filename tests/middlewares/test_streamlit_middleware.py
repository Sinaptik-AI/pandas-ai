"""Unit tests for the streamlit middleware class"""

from pandasai import PandasAI
from pandasai.llm.fake import FakeLLM
from pandasai.middlewares.streamlit import StreamlitMiddleware


class TestStreamlitMiddleware:
    """Unit tests for the streamlit middleware class"""

    def test_streamlit_middleware(self):
        """Test the streamlit middleware"""
        code = "plt.show()"
        middleware = StreamlitMiddleware()
        assert (
            middleware(code=code)
            == """import streamlit as st
st.pyplot(plt.gcf())"""
        )
        assert middleware.has_run

    def test_streamlit_middleware_optional_dependency(self, monkeypatch):
        """Test the streamlit middleware installs the optional dependency"""

        llm = FakeLLM("plt.show()")
        pandasai = PandasAI(llm, middlewares=[StreamlitMiddleware()])

        df = []

        pandasai(
            df,
            "Plot the histogram of countries showing for each the gpd, using different"
            "colors for each bar",
        )
        assert pandasai._additional_dependencies == [
            {"module": "streamlit", "name": "streamlit", "alias": "st"}
        ]
