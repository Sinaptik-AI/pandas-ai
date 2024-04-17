from typing import Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandasai.helpers.logger import Logger
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.code_generator import CodeGenerator
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class TestCodeGenerator:
    "Unit test for Code Generator"

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
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    def test_init(self, context, config):
        # Test the initialization of the CodeGenerator
        code_generator = CodeGenerator()
        assert isinstance(code_generator, CodeGenerator)

    @patch("pandasai.llm.fake.FakeLLM.call")
    def test_code_not_found_in_cache(self, mock_call, context, logger):
        # Test Flow : Code Not found in the cache
        code_generator = CodeGenerator()

        mock_get_promt = Mock(return_value=GeneratePythonCodePrompt)

        def mock_intermediate_values(key: str):
            if key == "output_type":
                return ""
            elif key == "viz_lib_helper":
                return "plotly"
            elif key == "get_prompt":
                return mock_get_promt

        def mock_execute_func(function, *args, **kwargs):
            if function == mock_get_promt:
                return mock_get_promt()
            return "Mocked LLM Generated Code"

        context.get = Mock(side_effect=mock_intermediate_values)
        context._cache = Mock()
        context._cache.get = Mock(return_value=None)

        mock_call.return_value = "```python test_output```"

        result = code_generator.execute(
            input="test_input", context=context, logger=logger
        )

        assert isinstance(code_generator, CodeGenerator)
        assert result.output == "test_output"
