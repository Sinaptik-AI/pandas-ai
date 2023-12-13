"""Unit tests for the SmartDatalake class"""
import json
import os
import sys
from typing import Optional
from unittest.mock import patch, Mock
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field
import pytest

from pandasai import SmartDataframe
from pandasai.exceptions import LLMNotFoundError
from pandasai.helpers.output_types import (
    DefaultOutputType,
    output_types_map,
    output_type_factory,
)
from pandasai.llm.fake import FakeLLM
from pandasai.prompts import AbstractPrompt, GeneratePythonCodePrompt
from pandasai.helpers.viz_library_types import (
    NoVizLibraryType,
    viz_lib_map,
    viz_lib_type_factory,
)
import logging


class TestSmartDataframe:
    """Unit tests for the SmartDatalake class"""

    def tearDown(self):
        for filename in [
            "df_test.parquet",
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

            def __init__(self, df: pd.DataFrame):
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
    def smart_dataframe_mocked_df(self, llm, sample_df, custom_head):
        smart_df = SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            custom_head=custom_head,
        )
        smart_df._core._df = Mock()
        return smart_df

    def test_init(self, smart_dataframe):
        assert smart_dataframe.table_name is None
        assert smart_dataframe.table_description is None
        assert smart_dataframe.dataframe is None

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

At the end, declare "result" var dict: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }



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
    def test_run_passing_output_type(self, llm, output_type, output_type_hint):
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

At the end, declare "result" var dict: {output_type_hint}



Generate python code and return full updated code:"""

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
        prompt_id = smart_dataframe.lake.last_prompt_id
        assert isinstance(prompt_id, UUID)

    def test_last_prompt_id_no_prompt(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.lake.last_prompt_id is None

    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_generator.CodeGenerator.execute",
        autospec=True,
    )
    def test_getters_are_accessible(
        self, mock_generate_code: Mock, smart_dataframe: SmartDataframe
    ):
        expected_code = "result = {'type': 'number', 'value': 1}"
        mock_generate_code.return_value = expected_code
        smart_dataframe.chat("What number comes before 2?")
        assert smart_dataframe.last_code_generated == expected_code

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
            == f"charts/{smart_dataframe.lake.last_prompt_id}.png"
        )

    def test_shortcut(self, smart_dataframe: SmartDataframe):
        assert callable(smart_dataframe.clean_data)
        with patch.object(smart_dataframe, "clean_data") as mock_clean_data:
            smart_dataframe.clean_data()
            mock_clean_data.assert_called_once()

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

    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_execution.CodeManager.execute_code",
        autospec=True,
    )
    def test_replace_correct_error_prompt(self, mock_execute, llm):
        # mock_execute should raise an exception only once
        mock_execute.side_effect = [Exception, None]

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
        df.chat("Will this work?")
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

    def test_updates_configs_with_setters(self, smart_dataframe: SmartDataframe):
        assert smart_dataframe.lake.config.enforce_privacy is False
        assert smart_dataframe.lake.config.use_error_correction_framework
        assert smart_dataframe.lake.config.custom_prompts == {}
        assert smart_dataframe.lake.config.save_charts is False
        assert smart_dataframe.lake.config.save_charts_path == "exports/charts"
        assert smart_dataframe.lake.config.custom_whitelisted_dependencies == []
        assert smart_dataframe.lake.config.max_retries == 3

        smart_dataframe.lake.config.enforce_privacy = True
        assert smart_dataframe.lake.config.enforce_privacy

        smart_dataframe.lake.config.use_error_correction_framework = False
        assert not smart_dataframe.lake.config.use_error_correction_framework

        smart_dataframe.lake.config.custom_prompts = {
            "generate_python_code": GeneratePythonCodePrompt()
        }
        assert smart_dataframe.lake.config.custom_prompts != {}

        smart_dataframe.lake.config.save_charts = True
        assert smart_dataframe.lake.config.save_charts

        smart_dataframe.lake.config.save_charts_path = "some/path"
        assert smart_dataframe.lake.config.save_charts_path == "some/path"

        smart_dataframe.lake.config.custom_whitelisted_dependencies = [
            "some_dependency"
        ]
        assert smart_dataframe.lake.config.custom_whitelisted_dependencies == [
            "some_dependency"
        ]

        smart_dataframe.lake.config.max_retries = 5
        assert smart_dataframe.lake.config.max_retries == 5

    def test_custom_head_getter(self, custom_head, smart_dataframe: SmartDataframe):
        assert smart_dataframe.head_df.custom_head.equals(custom_head)

    def test_custom_head_setter(self, custom_head, smart_dataframe: SmartDataframe):
        new_custom_head = (
            custom_head.copy().sample(frac=1, axis=1).reset_index(drop=True)
        )
        smart_dataframe.head_df.custom_head = new_custom_head
        assert new_custom_head.equals(smart_dataframe.head_df.custom_head)

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
        with patch("pandasai.connectors.pandas.PandasConnector", new=data_sampler):
            assert smart_dataframe.head_df.to_csv() == custom_head.to_csv(index=False)

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

At the end, declare "result" var dict: type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }
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
