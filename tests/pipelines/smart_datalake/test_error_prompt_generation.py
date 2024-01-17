from unittest.mock import MagicMock
import pandas as pd
from typing import Optional
import pytest
from pandasai.exceptions import InvalidLLMOutputType

from pandasai.llm.fake import FakeLLM

from pandasai.pipelines.smart_datalake_chat.error_correction_pipeline.error_prompt_generation import (
    ErrorPromptGeneration,
)
from pandasai.prompts.correct_error_prompt import CorrectErrorPrompt
from pandasai.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)
from pandasai.pipelines.pipeline_context import PipelineContext


class TestErrorPromptGeneration:
    "Unit test for Smart Data Lake Prompt Generation"

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

    def test_init(self):
        # Test the initialization of the PromptGeneration
        prompt_generation = ErrorPromptGeneration()
        assert isinstance(prompt_generation, ErrorPromptGeneration)

    def test_get_error_prompt_invalid_llm_output_type(self, context):
        error_prompt = ErrorPromptGeneration()

        # Mock the InvalidLLMOutputType exception
        mock_exception = MagicMock(spec=InvalidLLMOutputType)

        error_prompt = ErrorPromptGeneration()

        error_prompt.context = context

        # Call the method with the mock exception
        result = error_prompt._get_error_prompt(mock_exception)

        # Call the method with the mock exception
        result = error_prompt._get_error_prompt(mock_exception)

        # Assert that the CorrectOutputTypeErrorPrompt is returned
        assert isinstance(result, CorrectOutputTypeErrorPrompt)

    def test_get_error_prompt_other_exception(self, context):
        # Mock a generic exception
        mock_exception = MagicMock(spec=Exception)

        error_prompt = ErrorPromptGeneration()

        error_prompt.context = context

        # Call the method with the mock exception
        result = error_prompt._get_error_prompt(mock_exception)

        # Assert that the CorrectErrorPrompt is returned
        assert isinstance(result, CorrectErrorPrompt)
