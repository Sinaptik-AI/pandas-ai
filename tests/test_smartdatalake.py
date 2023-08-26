"""Unit tests for the SmartDatalake class"""
import os

from typing import Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandasai import SmartDataframe, SmartDatalake
from pandasai.helpers.code_manager import CodeManager
from pandasai.llm.fake import FakeLLM
from pandasai.middlewares import Middleware

from langchain import OpenAI


class TestSmartDatalake:
    """Unit tests for the SmartDatlake class"""

    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def smart_datalake(self, smart_dataframe: SmartDataframe):
        return smart_dataframe.lake

    @pytest.fixture
    def custom_middleware(self):
        class CustomMiddleware(Middleware):
            def run(self, code):
                return """def analyze_data(dfs):
    return { 'type': 'text', 'value': "Overwritten by middleware" }"""

        return CustomMiddleware

    def test_load_llm_with_pandasai_llm(self, smart_datalake: SmartDatalake, llm):
        smart_datalake._llm = None
        assert smart_datalake._llm is None

        smart_datalake._load_llm(llm)
        assert smart_datalake._llm == llm

    def test_load_llm_with_langchain_llm(self, smart_datalake: SmartDatalake, llm):
        langchain_llm = OpenAI(openai_api_key="fake_key")

        smart_datalake._llm = None
        assert smart_datalake._llm is None

        smart_datalake._load_llm(langchain_llm)
        assert smart_datalake._llm._langchain_llm == langchain_llm

    @patch.object(
        CodeManager,
        "execute_code",
        return_value={
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        },
    )
    def test_last_result_is_saved(self, _mocked_method, smart_datalake: SmartDatalake):
        assert smart_datalake.last_result is None

        smart_datalake.chat("How many countries are in the dataframe?")
        assert smart_datalake.last_result == {
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        }

    def test_middlewares(self, smart_dataframe: SmartDataframe, custom_middleware):
        middleware = custom_middleware()
        smart_dataframe.lake._code_manager._middlewares = [middleware]
        assert smart_dataframe.lake.middlewares == [middleware]
        assert (
            smart_dataframe.chat("How many countries are in the dataframe?")
            == "Overwritten by middleware"
        )
        assert middleware.has_run

    def test_retry_on_error_with_single_df(
        self, smart_datalake: SmartDatalake, smart_dataframe: SmartDataframe
    ):
        code = """def analyze_data(df):
    return { "type": "text", "value": "Hello World" }"""

        smart_dataframe._get_sample_head = Mock(
            return_value=pd.DataFrame(
                {
                    "country": ["China", "Japan", "Spain"],
                    "gdp": [654881226, 9009692259, 8446903488],
                    "happiness_index": [6.66, 7.16, 6.38],
                }
            )
        )

        smart_datalake._retry_run_code(
            code=code,
            e=Exception("Test error"),
        )

        assert (
            smart_datalake.last_prompt
            == """
You are provided with the following pandas DataFrames with the following metadata:

Dataframe dfs[0], with 10 rows and 3 columns.
This is the metadata of the dataframe dfs[0]:
country,gdp,happiness_index
China,654881226,6.66
Japan,9009692259,7.16
Spain,8446903488,6.38


The user asked the following question:


You generated this python code:
def analyze_data(df):
    return { "type": "text", "value": "Hello World" }

It fails with the following error:
Test error

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
"""  # noqa: E501
        )

    @patch("os.makedirs")
    def test_initialize(self, mock_makedirs, smart_datalake: SmartDatalake):
        smart_datalake.initialize()

        charts_dir = os.path.join(os.getcwd(), "exports", "charts")
        mock_makedirs.assert_any_call(charts_dir, mode=0o777, exist_ok=True)

        cache_dir = os.path.join(os.getcwd(), "cache")
        mock_makedirs.assert_any_call(cache_dir, mode=0o777, exist_ok=True)
