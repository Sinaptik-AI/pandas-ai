from typing import Optional

import pandas as pd
import pytest

from pandasai.connectors import PandasConnector
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.prompt_generation import PromptGeneration
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt
from pandasai.prompts.generate_python_code_with_sql import (
    GeneratePythonCodeWithSQLPrompt,
)


class TestPromptGeneration:
    "Unit test for Prompt Generation"

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
    def dataframe(self, sample_df):
        return PandasConnector({"original_df": sample_df})

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, dataframe, config):
        return PipelineContext([dataframe], config)

    def test_init(self):
        # Test the initialization of the PromptGeneration
        prompt_generation = PromptGeneration()
        assert isinstance(prompt_generation, PromptGeneration)

    def test_get_chat_prompt(self, context):
        # Test case 1: direct_sql is True
        prompt_generation = PromptGeneration()
        context.config.direct_sql = True

        gen_prompt = prompt_generation.get_chat_prompt(context)
        assert isinstance(gen_prompt, GeneratePythonCodeWithSQLPrompt)

        # Test case 2: direct_sql is False
        context.config.direct_sql = False

        gen_prompt = prompt_generation.get_chat_prompt(context)
        assert isinstance(gen_prompt, GeneratePythonCodePrompt)

    def test_get_chat_prompt_enforce_privacy(self, context):
        # Test case 1: direct_sql is True
        prompt_generation = PromptGeneration()
        context.config.enforce_privacy = True

        gen_prompt = prompt_generation.get_chat_prompt(context)
        assert isinstance(gen_prompt, GeneratePythonCodePrompt)
        assert (
            gen_prompt.to_string()
            == """dfs[0]:
  name: null
  description: null
  type: pd.DataFrame
  rows: 10
  columns: 3
  schema:
    fields:
    - name: country
      type: object
    - name: gdp
      type: object
    - name: happiness_index
      type: float64




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: 
type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }

```





Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.

If you are asked to plot a chart, use "matplotlib" for charts, save as png.


Generate python code and return full updated code:"""
        )

    def test_get_chat_prompt_enforce_privacy_false(self, context):
        # Test case 1: direct_sql is True
        prompt_generation = PromptGeneration()
        context.config.enforce_privacy = False

        gen_prompt = prompt_generation.get_chat_prompt(context)
        assert isinstance(gen_prompt, GeneratePythonCodePrompt)
        assert "samples" in gen_prompt.to_string()

    def test_get_chat_prompt_enforce_privacy_true_custom_head(self, context, sample_df):
        # Test case 1: direct_sql is True
        prompt_generation = PromptGeneration()
        context.config.enforce_privacy = True

        dataframe = PandasConnector({"original_df": sample_df}, custom_head=sample_df)
        context.dfs = [dataframe]

        gen_prompt = prompt_generation.get_chat_prompt(context)
        assert isinstance(gen_prompt, GeneratePythonCodePrompt)
        assert "samples" in gen_prompt.to_string()
