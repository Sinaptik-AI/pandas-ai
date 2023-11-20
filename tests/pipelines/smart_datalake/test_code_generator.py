from typing import Optional
from unittest.mock import Mock
import pandas as pd

import pytest
from pandasai.helpers.logger import Logger
from pandasai.helpers.output_types import output_type_factory
from pandasai.helpers.viz_library_types import viz_lib_type_factory
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt

from pandasai.smart_dataframe import SmartDataframe
from pandasai.pipelines.smart_datalake_chat.code_generator import CodeGenerator


class TestCodeGenerator:
    "Unit test for Smart Data Lake Code Generator"

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
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": True})

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

    def test_code_not_found_in_cache(self, context, logger):
        # Test Flow : Code Not found in the cache
        code_generator = CodeGenerator()

        mock_get_promt = Mock(return_value=GeneratePythonCodePrompt)

        def mock_intermediate_values(key: str):
            if key == "output_type_helper":
                return output_type_factory("DefaultOutputType")
            elif key == "viz_lib_helper":
                return viz_lib_type_factory("DefaultVizLibraryType")
            elif key == "get_prompt":
                return mock_get_promt

        def mock_execute_func(function, *args, **kwargs):
            if function == mock_get_promt:
                return mock_get_promt()
            return ["Mocked LLM Generated Code", "Mocked Reasoning", "Mocked Answer"]

        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)
        context._cache = Mock()
        context.cache.get = Mock(return_value=None)
        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(side_effect=mock_execute_func)

        code = code_generator.execute(input=None, context=context, logger=logger)

        assert isinstance(code_generator, CodeGenerator)
        assert code == "Mocked LLM Generated Code"
