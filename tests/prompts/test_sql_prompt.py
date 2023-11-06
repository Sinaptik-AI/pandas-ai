"""Unit tests for the correct error prompt class"""
import sys

import pandas as pd
import pytest
from pandasai import SmartDataframe
from pandasai.llm.fake import FakeLLM
from pandasai.prompts.direct_sql_prompt import DirectSQLPrompt
from pandasai.helpers.viz_library_types import (
    MatplotlibVizLibraryType,
    viz_lib_map,
    viz_lib_type_factory,
)
from pandasai.helpers.output_types import (
    output_type_factory,
    DefaultOutputType,
    output_types_map,
)


class TestDirectSqlPrompt:
    """Unit tests for the correct error prompt class"""

    @pytest.mark.parametrize(
        "save_charts_path,output_type_hint,viz_library_type_hint",
        [
            (
                "exports/charts",
                DefaultOutputType().template_hint,
                MatplotlibVizLibraryType().template_hint,
            ),
            (
                "custom/dir/for/charts",
                DefaultOutputType().template_hint,
                MatplotlibVizLibraryType().template_hint,
            ),
            *[
                (
                    "exports/charts",
                    output_type_factory(type_).template_hint,
                    viz_lib_type_factory(viz_type_).template_hint,
                )
                for type_ in output_types_map
                for viz_type_ in viz_lib_map
            ],
        ],
    )
    def test_direct_sql_prompt_with_params(
        self, save_charts_path, output_type_hint, viz_library_type_hint
    ):
        """Test that the __str__ method is implemented"""

        llm = FakeLLM("plt.show()")
        dfs = [
            SmartDataframe(
                pd.DataFrame({}),
                config={"llm": llm},
            )
        ]

        prompt = DirectSQLPrompt(tables=dfs)
        prompt.set_var("dfs", dfs)
        prompt.set_var("conversation", "What is the correct code?")
        prompt.set_var("output_type_hint", output_type_hint)
        prompt.set_var("save_charts_path", save_charts_path)
        prompt.set_var("viz_library_type", viz_library_type_hint)
        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        assert (
            prompt_content
            == f'''You are provided with the following samples of sql tables data:

<Tables>
<table>
</table>
<Tables>

<conversation>
What is the correct code?
</conversation>

You are provided with following function that executes the sql query, 
<Function>
def execute_sql_query(sql_query: str) -> pd.Dataframe
"""his method connect to the database executes the sql query and returns the dataframe"""
</Function>

This is the initial python function. Do not change the params.

```python
# TODO import all the dependencies required
import pandas as pd

def analyze_data() -> dict:
    """
    Analyze the data, using the provided dataframes (`dfs`).
    1. Prepare: generate sql query to get data for analysis (grouping, filtering, aggregating, etc.)
    2. Process: execute the query using execute method available to you which returns dataframe
    3. Analyze: Conducting the actual analysis (if the user asks to plot a chart you must save it as an image in temp_chart.png and not show the chart.)
    {viz_library_type_hint}
    At the end, return a dictionary of:
    {output_type_hint}
    """
```

Take a deep breath and reason step-by-step. Act as a senior data analyst.
In the answer, you must never write the "technical" names of the tables.
Based on the last message in the conversation:

- return the updated analyze_data function wrapped within `python `'''  # noqa: E501
        )
