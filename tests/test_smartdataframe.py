"""Unit tests for the SmartDatalake class"""
import sys
from typing import Optional
from unittest.mock import patch, Mock
from uuid import UUID

import pandas as pd
import pytest

from pandasai import SmartDataframe
from pandasai.exceptions import LLMNotFoundError
from pandasai.llm.fake import FakeLLM
from pandasai.middlewares import Middleware
from pandasai.callbacks import StdoutCallback
from pandasai.prompts import Prompt
from pandasai.helpers.cache import Cache

import logging


class TestSmartDataframe:

    """Unit tests for the SmartDatalake class"""

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
    def custom_middleware(self):
        class CustomMiddleware(Middleware):
            def run(self, code):
                return """def analyze_data(dfs):
    return { 'type': 'text', 'value': "Overwritten by middleware" }"""

        return CustomMiddleware

    def test_init(self, smart_dataframe):
        assert smart_dataframe._name is None
        assert smart_dataframe._description is None
        assert smart_dataframe._engine is not None
        assert smart_dataframe._df is not None

    def test_init_without_llm(self, sample_df):
        with pytest.raises(LLMNotFoundError):
            SmartDataframe(sample_df)

    def test_run(self, smart_dataframe: SmartDataframe, llm):
        llm._output = (
            "def analyze_data(dfs):\n    return { 'type': 'number', 'value': 1 }"
        )
        assert smart_dataframe.chat("What number comes before 2?") == 1

    def test_run_with_non_conversational_answer(
        self, smart_dataframe: SmartDataframe, llm
    ):
        llm._output = (
            "def analyze_data(dfs):\n    return { 'type': 'number', 'value': 1 + 1 }"
        )
        assert smart_dataframe.chat("What is the sum of 1 + 1?") == 2

    def test_callback(self, smart_dataframe: SmartDataframe):
        callback = StdoutCallback()
        smart_dataframe.callback = callback

        # mock on_code function
        with patch.object(callback, "on_code") as mock_on_code:
            smart_dataframe.chat("Give me sum of all gdps?")
            mock_on_code.assert_called()

    def test_run_code(self, smart_dataframe: SmartDataframe, llm):
        llm._output = """
def analyze_data(dfs):
    df = dfs[0]
    df['b'] = df['a'] + 1
    return { 'type': 'dataframe', 'value': df }
"""
        smart_dataframe = SmartDataframe(
            pd.DataFrame({"a": [1, 2, 3]}), config={"llm": llm, "enable_cache": False}
        )

        output_df = smart_dataframe.chat("Set column b to column a + 1")
        assert output_df["a"].tolist() == [1, 2, 3]
        assert output_df["b"].tolist() == [2, 3, 4]

    def test_run_with_privacy_enforcement(self, llm):
        df = pd.DataFrame({"country": []})
        df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
        df.enforce_privacy = True

        expected_prompt = """
You are provided with the following pandas DataFrames with the following metadata:

Dataframe dfs[0], with 0 rows and 1 columns.
This is the metadata of the dataframe dfs[0]:
country


This is the initial python code to be updated:
```python
# TODO import all the dependencies required
import pandas as pd

# Analyze the data
# 1. Prepare: Preprocessing and cleaning data if necessary
# 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
# 3. Analyze: Conducting the actual analysis (if generating a plot, create a figure and axes using plt.subplots() and save it to an image in exports/charts/temp_chart.png and do not show the chart.)
# 4. Output: return a dictionary of:
# - type (possible values "text", "number", "dataframe", "plot")
# - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
def analyze_data(self, dfs: list[pd.DataFrame]) -> dict:
   # Code goes here
    

# Declare a result variable
result = analyze_data(dfs)
```

Using the provided dataframes (`dfs`), update the python code based on the last user question:
User: How many countries are in the dataframe?

Updated code:
"""  # noqa: E501
        df.chat("How many countries are in the dataframe?")
        last_prompt = df.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = df.last_prompt.replace("\r\n", "\n")
        assert last_prompt == expected_prompt

    def test_extract_code(self, llm):
        code = """```python
result = {'happiness': 0.5, 'gdp': 0.8}
print(result)```"""
        assert (
            llm._extract_code(code)
            == "result = {'happiness': 0.5, 'gdp': 0.8}\nprint(result)"
        )

        code = """```
result = {'happiness': 1, 'gdp': 0.43}```"""
        assert llm._extract_code(code) == "result = {'happiness': 1, 'gdp': 0.43}"

        code = """```python<startCode>
result = {'happiness': 0.3, 'gdp': 5.5}<endCode>```"""
        assert llm._extract_code(code) == "result = {'happiness': 0.3, 'gdp': 5.5}"

        code = """<startCode>```python
result = {'happiness': 0.49, 'gdp': 25.5}```<endCode>"""
        assert llm._extract_code(code) == "result = {'happiness': 0.49, 'gdp': 25.5}"
        code = """<startCode>```python
result = {'happiness': 0.49, 'gdp': 25.5}```"""
        assert llm._extract_code(code) == "result = {'happiness': 0.49, 'gdp': 25.5}"

    def test_last_prompt_id(self, smart_dataframe: SmartDataframe):
        smart_dataframe.chat("How many countries are in the dataframe?")
        prompt_id = smart_dataframe.last_prompt_id
        assert isinstance(prompt_id, UUID)

    def test_last_prompt_id_no_prompt(self, smart_dataframe: SmartDataframe):
        with pytest.raises(AttributeError):
            smart_dataframe.last_prompt_id

    def test_add_middlewares(self, smart_dataframe: SmartDataframe, custom_middleware):
        middleware = custom_middleware()
        smart_dataframe.add_middlewares(middleware)
        assert (
            smart_dataframe.middlewares[len(smart_dataframe.middlewares) - 1]
            == middleware
        )

    def test_shortcut(self, smart_dataframe: SmartDataframe):
        smart_dataframe.chat = Mock(return_value="Hello world")
        smart_dataframe.clean_data()
        smart_dataframe.chat.assert_called_once()

    def test_replace_generate_code_prompt(self, llm):
        class CustomPrompt(Prompt):
            text: str = """{_num_rows} | $dfs[0].shape[1] | {_df_head} | {test}
{_conversation}"""

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        replacement_prompt = CustomPrompt(test="test value")
        df = SmartDataframe(
            pd.DataFrame(),
            config={
                "llm": llm,
                "enable_cache": False,
                "custom_prompts": {"generate_response": replacement_prompt},
            },
        )
        question = "Will this work?"
        df.chat(question)

        expected_last_prompt = replacement_prompt.to_string()
        expected_last_prompt = expected_last_prompt.replace(
            "$dfs[0].shape[1]", str(df.shape[1])
        )

        assert llm.last_prompt == expected_last_prompt

    def test_replace_correct_error_prompt(self, llm):
        class ReplacementPrompt(Prompt):
            text = "Custom prompt"

        replacement_prompt = ReplacementPrompt()
        df = SmartDataframe(
            pd.DataFrame(),
            config={
                "llm": llm,
                "custom_prompts": {"correct_error": replacement_prompt},
                "enable_cache": False,
            },
        )

        df._dl._retry_run_code("wrong code", Exception())
        expected_last_prompt = replacement_prompt.to_string()
        assert llm.last_prompt == expected_last_prompt

    def test_saves_logs(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.logs == []

        debug_msg = "Some debug log"
        info_msg = "Some info log"
        warning_msg = "Some warning log"
        error_msg = "Some error log"
        critical_msg = "Some critical log"

        smart_dataframe._dl._logger.log(debug_msg, level=logging.DEBUG)

        smart_dataframe._dl._logger.log(debug_msg, level=logging.DEBUG)
        smart_dataframe._dl._logger.log(info_msg)  # INFO should be default
        smart_dataframe._dl._logger.log(warning_msg, level=logging.WARNING)
        smart_dataframe._dl._logger.log(error_msg, level=logging.ERROR)
        smart_dataframe._dl._logger.log(critical_msg, level=logging.CRITICAL)
        logs = smart_dataframe.logs

        assert all("msg" in log and "level" in log for log in logs)
        assert {"msg": debug_msg, "level": logging.DEBUG} in logs
        assert {"msg": info_msg, "level": logging.INFO} in logs
        assert {"msg": warning_msg, "level": logging.WARNING} in logs
        assert {"msg": error_msg, "level": logging.ERROR} in logs
        assert {"msg": critical_msg, "level": logging.CRITICAL} in logs

    def test_updates_verbose_config_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.config.verbose is False

        smart_dataframe.verbose = True
        assert smart_dataframe.verbose is True
        assert smart_dataframe._dl._logger.verbose is True
        assert len(smart_dataframe._dl._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe._dl._logger._logger.handlers[0], logging.StreamHandler
        )

        smart_dataframe.verbose = False
        assert smart_dataframe.verbose is False
        assert smart_dataframe._dl._logger.verbose is False
        assert len(smart_dataframe._dl._logger._logger.handlers) == 0

    def test_updates_save_logs_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.save_logs is True

        smart_dataframe.save_logs = False
        assert smart_dataframe.save_logs is False
        assert smart_dataframe._dl._logger.save_logs is False
        assert len(smart_dataframe._dl._logger._logger.handlers) == 0

        smart_dataframe.save_logs = True
        assert smart_dataframe.save_logs is True
        assert smart_dataframe._dl._logger.save_logs is True
        assert len(smart_dataframe._dl._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe._dl._logger._logger.handlers[0], logging.FileHandler
        )

    def test_updates_enable_cache_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.enable_cache is False

        smart_dataframe.enable_cache = True
        assert smart_dataframe.enable_cache is True
        assert smart_dataframe._dl.enable_cache is True
        assert smart_dataframe._dl.cache is not None
        assert isinstance(smart_dataframe._dl._cache, Cache)

        smart_dataframe.enable_cache = False
        assert smart_dataframe.enable_cache is False
        assert smart_dataframe._dl.enable_cache is False
        assert smart_dataframe._dl.cache is None

    def test_updates_configs_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.callback is None
        assert smart_dataframe.enforce_privacy is False
        assert smart_dataframe.use_error_correction_framework is True
        assert smart_dataframe.custom_prompts == {}
        assert smart_dataframe.save_charts is False
        assert smart_dataframe.save_charts_path == "exports/charts"
        assert smart_dataframe.custom_whitelisted_dependencies == []
        assert smart_dataframe.max_retries == 3

        smart_dataframe.callback = lambda x: x
        assert smart_dataframe.callback is not None

        smart_dataframe.enforce_privacy = True
        assert smart_dataframe.enforce_privacy is True

        smart_dataframe.use_error_correction_framework = False
        assert smart_dataframe.use_error_correction_framework is False

        smart_dataframe.custom_prompts = {"generate_response": Prompt()}
        assert smart_dataframe.custom_prompts != {}

        smart_dataframe.save_charts = True
        assert smart_dataframe.save_charts is True

        smart_dataframe.save_charts_path = "some/path"
        assert smart_dataframe.save_charts_path == "some/path"

        smart_dataframe.custom_whitelisted_dependencies = ["some_dependency"]
        assert smart_dataframe.custom_whitelisted_dependencies == ["some_dependency"]

        smart_dataframe.max_retries = 5
        assert smart_dataframe.max_retries == 5

    def test_load_dataframe_from_list(self, smart_dataframe):
        input_data = [
            {"column1": 1, "column2": 4},
            {"column1": 2, "column2": 5},
            {"column1": 3, "column2": 6},
        ]

        smart_dataframe._load_df(input_data)

        assert isinstance(smart_dataframe._df, pd.DataFrame)

    def test_load_dataframe_from_dict(self, smart_dataframe):
        input_data = {"column1": [1, 2, 3], "column2": [4, 5, 6]}

        smart_dataframe._load_df(input_data)

        assert isinstance(smart_dataframe._df, pd.DataFrame)

    def test_load_dataframe_from_pandas_dataframe(self, smart_dataframe):
        pandas_df = pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})

        smart_dataframe._load_df(pandas_df)

        assert isinstance(smart_dataframe._df, pd.DataFrame)

    def test_load_dataframe_from_other_dataframe_type(self, smart_dataframe):
        # Simulating a Polars dataframe here
        polars_df = None

        smart_dataframe._load_df(polars_df)

        assert smart_dataframe._df is polars_df

    def test_import_csv_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pd,
            "read_csv",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.csv"

        df = smart_dataframe._import_from_file(file_path)

        assert isinstance(df, pd.DataFrame)

    def test_import_parquet_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pd,
            "read_parquet",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.parquet"

        df = smart_dataframe._import_from_file(file_path)

        assert isinstance(df, pd.DataFrame)

    def test_import_excel_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pd,
            "read_excel",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.xlsx"

        df = smart_dataframe._import_from_file(file_path)

        assert isinstance(df, pd.DataFrame)

    def test_invalid_file_format(self, smart_dataframe):
        with pytest.raises(ValueError):
            file_path = (
                "sample.txt"  # Note: should make a list of other not valid formats
            )
            # or make a for loop to check of the provided format from valid list?
            smart_dataframe._import_from_file(file_path)
