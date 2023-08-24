import pandas as pd
from pandasai import PandasAI, SmartDatalake
from pandasai.llm.fake import FakeLLM
import pytest
from unittest.mock import patch


class TestPandasAI:
    @pytest.fixture
    def llm(self):
        return FakeLLM()

    @pytest.fixture
    def df(self):
        return pd.DataFrame({"a": [1], "b": [4]})

    @pytest.fixture
    def pai(self, llm):
        return PandasAI(
            llm=llm,
            enable_cache=False,
        )

    def test_init(self, pai, llm):
        assert pai._config.llm == llm
        assert pai._config.callback is None
        assert pai._config.custom_prompts == {}
        assert pai._config.custom_whitelisted_dependencies == []
        assert pai._config.enable_cache is False
        assert pai._config.use_error_correction_framework is True
        assert pai._config.enforce_privacy is False
        assert pai._config.save_logs is True
        assert pai._config.save_charts is False
        assert pai._config.save_charts_path == ""
        assert pai._config.verbose is False
        assert pai._config.max_retries == 3
        assert pai._config.middlewares == []

    def test_logs(self, pai):
        assert pai.logs == []

    def test_last_prompt_id(self, pai):
        assert pai.last_prompt_id is None

    def test_last_prompt(self, pai):
        assert pai.last_prompt is None

    @patch.object(SmartDatalake, "chat", return_value="Answer")
    def test_run(self, _mocked_method, pai, df):
        assert pai.run(df, "Question") == "Answer"

    @patch.object(SmartDatalake, "chat", return_value="Answer")
    def test_call(self, _mocked_method, pai, df):
        assert pai(df, "Question") == "Answer"
