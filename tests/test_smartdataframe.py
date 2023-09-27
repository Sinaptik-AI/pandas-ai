"""Unit tests for the SmartDatalake class"""
import json
import os
import sys
from collections import defaultdict
from typing import Optional
from unittest.mock import patch, Mock
from uuid import UUID

import pandas as pd
import polars as pl
from pydantic import BaseModel, Field
import pytest

from pandasai import SmartDataframe
from pandasai.exceptions import LLMNotFoundError
from pandasai.llm.fake import FakeLLM
from pandasai.middlewares import Middleware
from pandasai.callbacks import StdoutCallback
from pandasai.prompts import AbstractPrompt, GeneratePythonCodePrompt
from pandasai.helpers.cache import Cache

import logging


class TestSmartDataframe:
    """Unit tests for the SmartDatalake class"""

    def tearDown(self):
        for filename in [
            "df_test.parquet",
            "df_test_polars.parquet",
            "df_duplicate.parquet",
        ]:
            if os.path.exists("cache/" + filename):
                os.remove("cache/" + filename)

        # Remove saved_dfs from pandasai.json
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            data["saved_dfs"] = []
        with open("pandasai.json", "w") as json_file:
            json.dump(data, json_file, indent=2)

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
    def sample_saved_dfs(self):
        return [
            {
                "name": "photo",
                "description": "Dataframe containing photo metadata",
                "sample": "filename,format,size\n1.jpg,JPEG,1240KB\n2.png,PNG,320KB",
                "import_path": "path/to/photo_data.parquet",
            }
        ]

    @pytest.fixture
    def sample_head(self, sample_df):
        return sample_df.head(5).sample(frac=1, axis=1).reset_index(drop=True)

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df, sample_head):
        return SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            sample_head=sample_head,
        )

    @pytest.fixture
    def smart_dataframe_mocked_df(self, llm, sample_df, sample_head):
        smart_df = SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            sample_head=sample_head,
        )
        smart_df._core._df = Mock()
        return smart_df

    @pytest.fixture
    def custom_middleware(self):
        class CustomMiddleware(Middleware):
            def run(self, code):
                return """def analyze_data(dfs):
    return { 'type': 'text', 'value': "Overwritten by middleware" }"""

        return CustomMiddleware

    def test_init(self, smart_dataframe):
        assert smart_dataframe._table_name is None
        assert smart_dataframe._table_description is None
        assert smart_dataframe.engine is not None
        assert smart_dataframe.dataframe is not None

    def test_init_without_llm(self, sample_df):
        with pytest.raises(LLMNotFoundError):
            SmartDataframe(sample_df, config={"llm": None})

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
You are provided with the following pandas DataFrames:

<dataframe>
Dataframe dfs[0], with 0 rows and 1 columns.
This is the metadata of the dataframe dfs[0]:
country
</dataframe>

<conversation>
User 1: How many countries are in the dataframe?
</conversation>

This is the initial python code to be updated:
```python
# TODO import all the dependencies required
import pandas as pd

def analyze_data(dfs: list[pd.DataFrame]) -> dict:
    \"\"\"
    Analyze the data
    1. Prepare: Preprocessing and cleaning data if necessary
    2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart save it to an image in exports/charts/temp_chart.png and do not show the chart.)
    4. Output: return a dictionary of:
    - type (possible values "text", "number", "dataframe", "plot")
    - value (can be a string, a dataframe or the path of the plot, NOT a dictionary)
    Example output: { "type": "text", "value": "The average loan amount is $15,000." }
    \"\"\"
```

Using the provided dataframes (`dfs`), update the python code based on the last question in the conversation.

Updated code:
"""  # noqa: E501
        df.chat("How many countries are in the dataframe?")
        last_prompt = df.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = df.last_prompt.replace("\r\n", "\n")
        assert last_prompt == expected_prompt

    def test_to_dict(self, smart_dataframe: SmartDataframe):
        expected_keys = ("country", "gdp", "happiness_index")

        result_dict = smart_dataframe.to_dict()

        assert isinstance(result_dict, dict)
        assert all(key in result_dict for key in expected_keys)

    @pytest.mark.parametrize(
        "to_dict_params,expected_passing_params,engine_type",
        [
            ({}, {"orient": "dict", "into": dict}, "pandas"),
            ({}, {"as_series": True}, "polars"),
            ({"orient": "dict"}, {"orient": "dict", "into": dict}, "pandas"),
            (
                {"orient": "dict", "into": defaultdict},
                {"orient": "dict", "into": defaultdict},
                "pandas",
            ),
            ({"as_series": False}, {"as_series": False}, "polars"),
            (
                {"as_series": False, "orient": "dict", "into": defaultdict},
                {"as_series": False},
                "polars",
            ),
        ],
    )
    def test_to_dict_passing_parameters(
        self,
        smart_dataframe_mocked_df: SmartDataframe,
        to_dict_params,
        engine_type,
        expected_passing_params,
    ):
        smart_dataframe_mocked_df._engine = engine_type
        smart_dataframe_mocked_df.to_dict(**to_dict_params)
        # noinspection PyUnresolvedReferences
        smart_dataframe_mocked_df.dataframe.to_dict.assert_called_once_with(
            **expected_passing_params
        )

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

    def test_last_prompt_id(self, smart_dataframe: SmartDataframe):
        smart_dataframe.chat("How many countries are in the dataframe?")
        prompt_id = smart_dataframe.last_prompt_id
        assert isinstance(prompt_id, UUID)

    def test_last_prompt_id_no_prompt(self, smart_dataframe: SmartDataframe):
        with pytest.raises(AttributeError):
            smart_dataframe.last_prompt_id

    def test_getters_are_accessible(self, smart_dataframe: SmartDataframe, llm):
        llm._output = (
            "def analyze_data(dfs):\n    return {'type': 'number', 'value': 1}"
        )
        smart_dataframe.chat("What number comes before 2?")
        assert (
            smart_dataframe.last_code_generated
            == "def analyze_data(dfs):\n    return {'type': 'number', 'value': 1}"
        )

    def test_save_chart_non_default_dir(
        self, smart_dataframe: SmartDataframe, llm, sample_df
    ):
        """
        Test chat with `SmartDataframe` with custom `save_charts_path`.

        Script:
            1) Ask `SmartDataframe` to build a chart and save it in
               a custom directory;
            2) Check if substring representing the directory present in
               `llm.last_prompt`.
            3) Check if the code has had a call of `plt.savefig()` passing
               the custom directory.

        Notes:
            1) Mock `import_dependency()` util-function to avoid the
               actual calls to `matplotlib.pyplot`.
            2) The `analyze_data()` function in the code fixture must have
               `"type": None` in the result dict. Otherwise, if it had
               `"type": "plot"` (like it has in practice), `_format_results()`
               method from `SmartDatalake` object would try to read the image
               with `matplotlib.image.imread()` and this test would fail.
               Those calls to `matplotlib.image` are unmockable because of
               imports inside the function scope, not in the top of a module.
               @TODO: figure out if we can just move the imports beyond to
                      make it possible to mock out `matplotlib.image`
        """
        llm._output = """
import pandas as pd
import matplotlib.pyplot as plt
def analyze_data(dfs: list[pd.DataFrame]) -> dict:
    df = dfs[0].nlargest(5, 'happiness_index')
    
    plt.figure(figsize=(8, 6))
    plt.pie(df['happiness_index'], labels=df['country'], autopct='%1.1f%%')
    plt.title('Happiness Index for the 5 Happiest Countries')
    plt.savefig('custom-dir/output_charts/temp_chart.png')
    plt.close()
    
    return {"type": None, "value": "custom-dir/output_charts/temp_chart.png"}
result = analyze_data(dfs)
"""
        with patch(
            "pandasai.helpers.code_manager.import_dependency"
        ) as import_dependency_mock:
            smart_dataframe = SmartDataframe(
                sample_df,
                config={
                    "llm": llm,
                    "enable_cache": False,
                    "save_charts": True,
                    "save_charts_path": "custom-dir/output_charts/",
                },
            )

            smart_dataframe.chat("Plot pie-chart the 5 happiest countries")

        assert "custom-dir/output_charts/temp_chart.png" in llm.last_prompt
        plt_mock = getattr(import_dependency_mock.return_value, "matplotlib.pyplot")
        assert plt_mock.savefig.called
        assert (
            plt_mock.savefig.call_args.args[0]
            == "custom-dir/output_charts/temp_chart.png"
        )

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
        class CustomPrompt(AbstractPrompt):
            template: str = """{test} || {dfs[0].shape[1]} || {conversation}"""

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        replacement_prompt = CustomPrompt(test="test value")
        df = SmartDataframe(
            pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
            config={
                "llm": llm,
                "enable_cache": False,
                "custom_prompts": {"generate_python_code": replacement_prompt},
            },
        )
        question = "Will this work?"
        df.chat(question)

        expected_last_prompt = replacement_prompt.to_string()
        assert llm.last_prompt == expected_last_prompt

    def test_replace_correct_error_prompt(self, llm):
        class ReplacementPrompt(AbstractPrompt):
            @property
            def template(self):
                return "Custom prompt"

        replacement_prompt = ReplacementPrompt()
        df = SmartDataframe(
            pd.DataFrame(),
            config={
                "llm": llm,
                "custom_prompts": {"correct_error": replacement_prompt},
                "enable_cache": False,
            },
        )

        df.lake._retry_run_code("wrong code", Exception())
        expected_last_prompt = replacement_prompt.to_string()
        assert llm.last_prompt == expected_last_prompt

    def test_saves_logs(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.logs == []

        debug_msg = "Some debug log"
        info_msg = "Some info log"
        warning_msg = "Some warning log"
        error_msg = "Some error log"
        critical_msg = "Some critical log"

        smart_dataframe.lake.logger.log(debug_msg, level=logging.DEBUG)

        smart_dataframe.lake.logger.log(debug_msg, level=logging.DEBUG)
        smart_dataframe.lake.logger.log(info_msg)  # INFO should be default
        smart_dataframe.lake.logger.log(warning_msg, level=logging.WARNING)
        smart_dataframe.lake.logger.log(error_msg, level=logging.ERROR)
        smart_dataframe.lake.logger.log(critical_msg, level=logging.CRITICAL)
        logs = smart_dataframe.logs

        assert all("msg" in log and "level" in log for log in logs)
        assert {"msg": debug_msg, "level": logging.DEBUG} in logs
        assert {"msg": info_msg, "level": logging.INFO} in logs
        assert {"msg": warning_msg, "level": logging.WARNING} in logs
        assert {"msg": error_msg, "level": logging.ERROR} in logs
        assert {"msg": critical_msg, "level": logging.CRITICAL} in logs

    def test_updates_verbose_config_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.verbose is False

        smart_dataframe.verbose = True
        assert smart_dataframe.verbose is True
        assert smart_dataframe.lake._logger.verbose is True
        assert len(smart_dataframe.lake._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe.lake._logger._logger.handlers[0], logging.StreamHandler
        )

        smart_dataframe.verbose = False
        assert smart_dataframe.verbose is False
        assert smart_dataframe.lake._logger.verbose is False
        assert len(smart_dataframe.lake._logger._logger.handlers) == 0

    def test_updates_save_logs_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.save_logs is True

        smart_dataframe.save_logs = False
        assert smart_dataframe.save_logs is False
        assert smart_dataframe.lake._logger.save_logs is False
        assert len(smart_dataframe.lake._logger._logger.handlers) == 0

        smart_dataframe.save_logs = True
        assert smart_dataframe.save_logs is True
        assert smart_dataframe.lake._logger.save_logs is True
        assert len(smart_dataframe.lake._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe.lake._logger._logger.handlers[0], logging.FileHandler
        )

    def test_updates_enable_cache_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.enable_cache is False

        smart_dataframe.enable_cache = True
        assert smart_dataframe.enable_cache is True
        assert smart_dataframe.lake.enable_cache is True
        assert smart_dataframe.lake.cache is not None
        assert isinstance(smart_dataframe.lake._cache, Cache)

        smart_dataframe.enable_cache = False
        assert smart_dataframe.enable_cache is False
        assert smart_dataframe.lake.enable_cache is False
        assert smart_dataframe.lake.cache is None

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

        smart_dataframe.custom_prompts = {
            "generate_python_code": GeneratePythonCodePrompt()
        }
        assert smart_dataframe.custom_prompts != {}

        smart_dataframe.save_charts = True
        assert smart_dataframe.save_charts is True

        smart_dataframe.save_charts_path = "some/path"
        assert smart_dataframe.save_charts_path == "some/path"

        smart_dataframe.custom_whitelisted_dependencies = ["some_dependency"]
        assert smart_dataframe.custom_whitelisted_dependencies == ["some_dependency"]

        smart_dataframe.max_retries = 5
        assert smart_dataframe.max_retries == 5

    def test_sample_head_getter(self, sample_head, smart_dataframe: SmartDataframe):
        assert smart_dataframe.sample_head.equals(sample_head)

    def test_sample_head_setter(self, sample_head, smart_dataframe: SmartDataframe):
        new_sample_head = (
            sample_head.copy().sample(frac=1, axis=1).reset_index(drop=True)
        )
        smart_dataframe.sample_head = new_sample_head
        assert new_sample_head.equals(smart_dataframe.sample_head)

    def test_load_dataframe_from_list(self, smart_dataframe):
        input_data = [
            {"column1": 1, "column2": 4},
            {"column1": 2, "column2": 5},
            {"column1": 3, "column2": 6},
        ]

        smart_dataframe._load_dataframe(input_data)

        assert isinstance(smart_dataframe.dataframe, pd.DataFrame)

    def test_load_dataframe_from_dict(self, smart_dataframe):
        input_data = {"column1": [1, 2, 3], "column2": [4, 5, 6]}

        smart_dataframe._load_dataframe(input_data)

        assert isinstance(smart_dataframe.dataframe, pd.DataFrame)

    def test_load_dataframe_from_pandas_dataframe(self, smart_dataframe):
        pandas_df = pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})

        smart_dataframe._load_dataframe(pandas_df)

        assert isinstance(smart_dataframe.dataframe, pd.DataFrame)

    def test_load_dataframe_from_saved_dfs(self, sample_saved_dfs, mocker):
        expected_df = pd.DataFrame(
            {
                "filename": ["photo1.jpg", "photo2.jpg"],
                "format": ["JPEG", "PNG"],
                "size": ["1240KB", "320KB"],
            }
        )
        mocker.patch.object(pd, "read_parquet", return_value=expected_df)

        mocker.patch.object(
            json,
            "load",
            return_value={"saved_dfs": sample_saved_dfs},
        )

        saved_df_name = "photo"
        smart_dataframe = SmartDataframe(saved_df_name)

        assert isinstance(smart_dataframe.dataframe, pd.DataFrame)
        assert smart_dataframe.table_name == saved_df_name
        assert smart_dataframe.dataframe.equals(expected_df)

    def test_load_dataframe_from_other_dataframe_type(self, smart_dataframe):
        polars_df = pl.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})

        smart_dataframe._load_dataframe(polars_df)

        print(smart_dataframe.dataframe)
        print(polars_df)

        assert isinstance(smart_dataframe.dataframe, pl.DataFrame)
        assert smart_dataframe.dataframe.frame_equal(polars_df)

    def test_import_csv_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pd,
            "read_parquet",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.parquet"

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

        expected_df = pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})
        assert df.equals(expected_df)

    @pytest.mark.parametrize("file_path", ["sample.txt", "sample.docx", "sample.pdf"])
    def test_invalid_file_format(self, smart_dataframe, file_path):
        with pytest.raises(ValueError):
            smart_dataframe._import_from_file(file_path)

    def test_import_pandas_series(self, llm):
        pandas_series = pd.Series([1, 2, 3])

        smart_dataframe = SmartDataframe(pandas_series, config={"llm": llm})

        assert isinstance(smart_dataframe.dataframe, pd.DataFrame)
        assert smart_dataframe.dataframe.equals(pd.DataFrame({0: [1, 2, 3]}))

    def test_save_pandas_dataframe(self, llm):
        with open("pandasai.json", "r") as json_file:
            backup_pandasai = json_file.read()

        # Create an instance of SmartDataframe
        pandas_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df_object = SmartDataframe(
            pandas_df,
            name="df_test",
            description="Test description",
            config={"llm": llm, "enable_cache": False},
        )

        # Call the save function
        df_object.save()

        # Verify that the data was saved correctly
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            assert data["saved_dfs"][0]["name"] == "df_test"

        with open("pandasai.json", "w") as json_file:
            json_file.write(backup_pandasai)

    def test_save_pandas_dataframe_with_name(self, llm):
        with open("pandasai.json", "r") as json_file:
            backup_pandasai = json_file.read()

        # Create an instance of SmartDataframe
        pandas_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        df_object = SmartDataframe(
            pandas_df,
            name="df_test",
            description="Test description",
            config={"llm": llm, "enable_cache": False},
        )

        # Call the save function
        df_object.save("custom_name")

        # Verify that the data was saved correctly
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            assert data["saved_dfs"][0]["name"] == "custom_name"

        with open("pandasai.json", "w") as json_file:
            json_file.write(backup_pandasai)

    def test_save_polars_dataframe(self, llm):
        with open("pandasai.json", "r") as json_file:
            backup_pandasai = json_file.read()

        # Create an instance of SmartDataframe
        polars_df = pl.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})
        df_object = SmartDataframe(
            polars_df,
            name="df_test_polars",
            description="Test description",
            config={"llm": llm, "enable_cache": False},
        )

        # Call the save function
        df_object.save()

        # Verify that the data was saved correctly
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            assert data["saved_dfs"][0]["name"] == "df_test_polars"

        # recover file for next test case
        with open("pandasai.json", "w") as json_file:
            json_file.write(backup_pandasai)

    def test_save_pandas_dataframe_duplicate_name(self, llm):
        with open("pandasai.json", "r") as json_file:
            backup_pandasai = json_file.read()

        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        # Create instances of SmartDataframe
        df_object1 = SmartDataframe(
            df,
            name="df_duplicate",
            description="Description 1",
            config={"llm": llm, "enable_cache": False},
        )
        df_object2 = SmartDataframe(
            df,
            name="df_duplicate",
            description="Description 2",
            config={"llm": llm, "enable_cache": False},
        )

        # Call the save function for the first instance
        df_object1.save()

        # Attempt to save the second instance and check for ValueError
        with pytest.raises(ValueError, match="Duplicate dataframe found: df_duplicate"):
            df_object2.save()

        # Recover file for next test case
        with open("pandasai.json", "w") as json_file:
            json_file.write(backup_pandasai)

    def test_save_pandas_no_name(self, llm):
        with open("pandasai.json", "r") as json_file:
            backup_pandasai = json_file.read()

        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="No Name", config={"llm": llm, "enable_cache": False}
        )

        # Mock the hashlib.sha256() method
        with patch("hashlib.sha256") as mock_sha256:
            # Set the return value of the hexdigest() method
            mock_sha256.return_value.hexdigest.return_value = "mocked_hash"

            # Call the save() method
            df_object.save()

            # Check that hashlib.sha256() was called with the correct argument
            mock_sha256.assert_called_with(df_object.head_csv.encode())

        # Verify that the data was saved correctly
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            assert data["saved_dfs"][0]["name"] == "mocked_hash"

        # Recover file for next test case
        with open("pandasai.json", "w") as json_file:
            json_file.write(backup_pandasai)

    def test_pydantic_validate(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is True

    def test_pydantic_validate_false(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": ["Test", "Test2", "Test3", "Test4"], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is False

    def test_pydantic_validate_polars(self, llm):
        # Create a sample DataFrame
        df = pl.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)
        assert validation_result.passed is True

    def test_pydantic_validate_false_one_record(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, "test", 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)
        assert (
            validation_result.passed is False and len(validation_result.errors()) == 1
        )

    def test_pydantic_validate_complex_schema(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int = Field(..., gt=5)
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is False

        class TestSchema(BaseModel):
            A: int = Field(..., lt=5)
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is True
