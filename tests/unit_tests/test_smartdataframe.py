"""Unit tests for the SmartDatalake class"""
import json
import logging
import os
import sys
from collections import defaultdict
from typing import Optional
from unittest.mock import Mock, patch
from uuid import UUID

import pandas as pd
import polars as pl
import pytest
from pydantic import BaseModel, Field

import pandasai
from pandasai import SmartDataframe
from pandasai.exceptions import LLMNotFoundError
from pandasai.helpers.cache import Cache
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.output_types import (
    DefaultOutputType,
    output_type_factory,
    output_types_map,
)
from pandasai.helpers.viz_library_types import (
    NoVizLibraryType,
    viz_lib_map,
    viz_lib_type_factory,
)
from pandasai.llm.fake import FakeLLM
from pandasai.prompts import AbstractPrompt, GeneratePythonCodePrompt


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
    def data_sampler(self):
        class DataSampler:
            df = None

            def __init__(self, df: DataFrameType):
                self.df = df

            def sample(self, _n: int = 5):
                return self.df

        return DataSampler

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
    def custom_head(self, sample_df: pd.DataFrame):
        return pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df, custom_head):
        return SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            custom_head=custom_head,
        )

    @pytest.fixture
    def llm_result_mocks(self, custom_head):
        result_template = "result = {{ 'type': '{type}', 'value': {value} }}"

        return {
            "number": result_template.format(type="number", value=1),
            "string": result_template.format(type="string", value="'Test'"),
            "plot": result_template.format(type="plot", value="'temp_plot.png'"),
            "dataframe": result_template.format(type="dataframe", value=custom_head),
        }

    @pytest.fixture
    def smart_dataframe_mocked_df(self, llm, sample_df, custom_head):
        smart_df = SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            custom_head=custom_head,
        )
        smart_df._core._df = Mock()
        return smart_df

    def test_init(self, smart_dataframe):
        assert smart_dataframe._table_name is None
        assert smart_dataframe._table_description is None
        assert smart_dataframe.engine is not None
        assert smart_dataframe.dataframe is not None

    def test_init_without_llm(self, sample_df):
        with pytest.raises(LLMNotFoundError):
            SmartDataframe(sample_df, config={"llm": "-"})

    def test_run(self, smart_dataframe: SmartDataframe, llm):
        llm._output = "result = { 'type': 'number', 'value': 1 }"
        assert smart_dataframe.chat("What number comes before 2?") == 1

    def test_run_with_non_conversational_answer(
        self, smart_dataframe: SmartDataframe, llm
    ):
        llm._output = "result = { 'type': 'number', 'value': 1 + 1 }"
        assert smart_dataframe.chat("What is the sum of 1 + 1?") == 2

    def test_run_code(self, smart_dataframe: SmartDataframe, llm):
        llm._output = """
df = dfs[0]
df['b'] = df['a'] + 1
result = { 'type': 'dataframe', 'value': df }
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

        expected_prompt = """<dataframe>
dfs[0]:0x1
country
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }
```

Q: How many countries are in the dataframe?
Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.



Generate python code and return full updated code:"""  # noqa: E501
        df.chat("How many countries are in the dataframe?")
        last_prompt = df.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = df.last_prompt.replace("\r\n", "\n")

        assert last_prompt == expected_prompt

    @pytest.mark.parametrize(
        "output_type,output_type_hint",
        [
            (None, DefaultOutputType().template_hint),
            *[
                (type_, output_type_factory(type_).template_hint)
                for type_ in output_types_map
            ],
        ],
    )
    @patch("pandasai.responses.response_parser.ResponseParser.parse", autospec=True)
    @patch("pandasai.helpers.query_exec_tracker.QueryExecTracker._format_response")
    def test_run_passing_output_type(
        self,
        _format_response_mock,
        parser_mock,
        llm,
        llm_result_mocks,
        output_type,
        output_type_hint,
    ):
        df = pd.DataFrame({"country": []})
        df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})

        expected_prompt = f"""<dataframe>
dfs[0]:0x1
country
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: {output_type_hint}
```

Q: How many countries are in the dataframe?
Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.



Generate python code and return full updated code:"""
        parser_mock.return_value = Mock()
        _format_response_mock.return_value = Mock()
        type_ = output_type if output_type is not None else "string"
        llm._output = llm_result_mocks[type_]

        df.chat("How many countries are in the dataframe?", output_type=output_type)
        last_prompt = df.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = df.last_prompt.replace("\r\n", "\n")
        assert last_prompt == expected_prompt

    @pytest.mark.parametrize(
        "output_type_to_pass,output_type_returned",
        [
            ("number", "string"),
            ("string", "number"),
        ],
    )
    def test_run_incorrect_output_type_returned(
        self,
        smart_dataframe: SmartDataframe,
        llm,
        sample_df,
        output_type_to_pass,
        output_type_returned,
    ):
        llm._output = f"""highest_gdp = dfs[0]['gdp'].max()
result = {{ 'type': '{output_type_returned}', 'value': highest_gdp }}
"""
        smart_dataframe = SmartDataframe(
            sample_df, config={"llm": llm, "enable_cache": False}
        )

        smart_dataframe.chat(
            "What is the highest GDP?", output_type=output_type_to_pass
        )
        expected_log = (
            f"The result dict contains inappropriate 'type'. "
            f"Expected '{output_type_to_pass}', actual "
            f"'{output_type_returned}'"
        )
        assert any((expected_log in log.get("msg") for log in smart_dataframe.logs))

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
        llm._output = "result = {'type': 'number', 'value': 1}"
        smart_dataframe.chat("What number comes before 2?")
        assert (
            smart_dataframe.last_code_generated
            == "result = {'type': 'number', 'value': 1}"
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

df = dfs[0].nlargest(5, 'happiness_index')

plt.figure(figsize=(8, 6))
plt.pie(df['happiness_index'], labels=df['country'], autopct='%1.1f%%')
plt.title('Happiness Index for the 5 Happiest Countries')
plt.savefig('temp_chart.png')
plt.close()

result = {"type": None, "value": "temp_chart.png"}
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
                    "save_charts_path": "charts",
                },
            )

            smart_dataframe.chat("Plot pie-chart the 5 happiest countries")

        plt_mock = getattr(import_dependency_mock.return_value, "matplotlib.pyplot")
        assert plt_mock.savefig.called
        assert (
            plt_mock.savefig.call_args.args[0]
            == f"charts/{smart_dataframe.last_prompt_id}.png"
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
        with patch.object(smart_dataframe.lake.logger, "_calculate_time_diff"):
            smart_dataframe.lake.logger._calculate_time_diff.return_value = 0

            assert smart_dataframe.logs == []

            debug_msg = "Some debug log"
            info_msg = "Some info log"
            warning_msg = "Some warning log"
            error_msg = "Some error log"
            critical_msg = "Some critical log"

            smart_dataframe.lake.logger.log(debug_msg, level=logging.DEBUG)
            smart_dataframe.lake.logger.log(info_msg)  # INFO should be default
            smart_dataframe.lake.logger.log(warning_msg, level=logging.WARNING)
            smart_dataframe.lake.logger.log(error_msg, level=logging.ERROR)
            smart_dataframe.lake.logger.log(critical_msg, level=logging.CRITICAL)
            logs = smart_dataframe.logs

            assert len(logs) == 5

            assert all(
                ("msg" in log and "level" in log and "time" in log and "source" in log)
                for log in logs
            )
            assert {
                "msg": debug_msg,
                "level": "DEBUG",
                "time": 0,
                "source": "TestSmartDataframe",
            } in logs
            assert {
                "msg": info_msg,
                "level": "INFO",
                "time": 0,
                "source": "TestSmartDataframe",
            } in logs
            assert {
                "msg": warning_msg,
                "level": "WARNING",
                "time": 0,
                "source": "TestSmartDataframe",
            } in logs
            assert {
                "msg": error_msg,
                "level": "ERROR",
                "time": 0,
                "source": "TestSmartDataframe",
            } in logs
            assert {
                "msg": critical_msg,
                "level": "CRITICAL",
                "time": 0,
                "source": "TestSmartDataframe",
            } in logs

    def test_updates_verbose_config_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.verbose is False

        smart_dataframe.verbose = True
        assert smart_dataframe.verbose
        assert smart_dataframe.lake._logger.verbose
        assert len(smart_dataframe.lake._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe.lake._logger._logger.handlers[0], logging.StreamHandler
        )

        smart_dataframe.verbose = False
        assert not smart_dataframe.verbose
        assert smart_dataframe.lake._logger.verbose is False
        assert len(smart_dataframe.lake._logger._logger.handlers) == 0

    def test_updates_save_logs_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.save_logs

        smart_dataframe.save_logs = False
        assert not smart_dataframe.save_logs
        assert not smart_dataframe.lake._logger.save_logs
        assert len(smart_dataframe.lake._logger._logger.handlers) == 0

        smart_dataframe.save_logs = True
        assert smart_dataframe.save_logs
        assert smart_dataframe.lake._logger.save_logs
        assert len(smart_dataframe.lake._logger._logger.handlers) == 1
        assert isinstance(
            smart_dataframe.lake._logger._logger.handlers[0], logging.FileHandler
        )

    def test_updates_enable_cache_config_with_setters(
        self, smart_dataframe: SmartDataframe
    ):
        assert smart_dataframe.enable_cache is False

        smart_dataframe.enable_cache = True
        assert smart_dataframe.enable_cache
        assert smart_dataframe.lake.enable_cache
        assert smart_dataframe.lake.cache is not None
        assert isinstance(smart_dataframe.lake._cache, Cache)

        smart_dataframe.enable_cache = False
        assert not smart_dataframe.enable_cache
        assert smart_dataframe.lake.enable_cache is False
        assert smart_dataframe.lake.cache is None

    def test_updates_configs_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.enforce_privacy is False
        assert smart_dataframe.use_error_correction_framework
        assert smart_dataframe.custom_prompts == {}
        assert smart_dataframe.save_charts is False
        assert smart_dataframe.save_charts_path == "exports/charts"
        assert smart_dataframe.custom_whitelisted_dependencies == []
        assert smart_dataframe.max_retries == 3

        smart_dataframe.enforce_privacy = True
        assert smart_dataframe.enforce_privacy

        smart_dataframe.use_error_correction_framework = False
        assert not smart_dataframe.use_error_correction_framework

        smart_dataframe.custom_prompts = {
            "generate_python_code": GeneratePythonCodePrompt()
        }
        assert smart_dataframe.custom_prompts != {}

        smart_dataframe.save_charts = True
        assert smart_dataframe.save_charts

        smart_dataframe.save_charts_path = "some/path"
        assert smart_dataframe.save_charts_path == "some/path"

        smart_dataframe.custom_whitelisted_dependencies = ["some_dependency"]
        assert smart_dataframe.custom_whitelisted_dependencies == ["some_dependency"]

        smart_dataframe.max_retries = 5
        assert smart_dataframe.max_retries == 5

    def test_custom_head_getter(self, custom_head, smart_dataframe: SmartDataframe):
        assert smart_dataframe.custom_head.equals(custom_head)

    def test_custom_head_setter(self, custom_head, smart_dataframe: SmartDataframe):
        new_custom_head = (
            custom_head.copy().sample(frac=1, axis=1).reset_index(drop=True)
        )
        smart_dataframe.custom_head = new_custom_head
        assert new_custom_head.equals(smart_dataframe.custom_head)

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
        mocker.patch.object(pandasai.pandas, "read_parquet", return_value=expected_df)

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

        assert isinstance(smart_dataframe.dataframe, pl.DataFrame)
        assert smart_dataframe.dataframe.frame_equal(polars_df)

    def test_import_csv_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pandasai.pandas,
            "read_parquet",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.parquet"

        df = smart_dataframe._import_from_file(file_path)

        assert isinstance(df, pd.DataFrame)

    def test_import_parquet_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pandasai.pandas,
            "read_parquet",
            return_value=pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]}),
        )

        file_path = "sample.parquet"

        df = smart_dataframe._import_from_file(file_path)

        assert isinstance(df, pd.DataFrame)

    def test_import_excel_file(self, smart_dataframe, mocker):
        mocker.patch.object(
            pandasai.pandas,
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

        assert validation_result.passed

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
        assert validation_result.passed

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

        assert validation_result.passed

    def test_head_csv_with_custom_head(
        self, custom_head, data_sampler, smart_dataframe: SmartDataframe
    ):
        with patch("pandasai.smart_dataframe.DataSampler", new=data_sampler):
            assert smart_dataframe.head_csv == custom_head.to_csv(index=False)

    @pytest.mark.parametrize(
        "viz_library_type,viz_library_type_hint",
        [
            (None, NoVizLibraryType().template_hint),
            *[
                (type_, viz_lib_type_factory(type_).template_hint)
                for type_ in viz_lib_map
            ],
        ],
    )
    def test_run_passing_viz_library_type(
        self, llm, viz_library_type, viz_library_type_hint
    ):
        df = pd.DataFrame({"country": []})
        df = SmartDataframe(
            df,
            config={
                "llm": llm,
                "enable_cache": False,
                "data_viz_library": viz_library_type,
            },
        )

        expected_prompt = (
            """<dataframe>
dfs[0]:0x1
country
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }
```

Q: Plot the histogram of countries showing for each the gdp with distinct bar colors
Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.
%s


Generate python code and return full updated code:"""  # noqa: E501
            % viz_library_type_hint
        )

        df.chat(
            "Plot the histogram of countries showing for each the gdp"
            " with distinct bar colors"
        )
        last_prompt = df.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = df.last_prompt.replace("\r\n", "\n")

        assert last_prompt == expected_prompt
