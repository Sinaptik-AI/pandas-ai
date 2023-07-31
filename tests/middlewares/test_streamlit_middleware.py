"""Unit tests for the streamlit middleware class"""

import pandas as pd

from pandasai.smart_datalake import SmartDatalake
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

    def test_streamlit_middleware_optional_dependency(self, mock_json_load):
        """Test the streamlit middleware installs the optional dependency"""

        mock_json_load.return_value = {}

        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        llm = FakeLLM("plt.show()")
        dl = SmartDatalake(
            [df],
            config={
                "llm": llm,
                "middlewares": [StreamlitMiddleware()],
                "enable_cache": False,
            },
        )

        dl.chat(
            "Plot the histogram of countries showing for each the gpd, using different"
            "colors for each bar",
        )
        assert dl._code_manager._additional_dependencies == [
            {"module": "streamlit", "name": "streamlit", "alias": "st"}
        ]
