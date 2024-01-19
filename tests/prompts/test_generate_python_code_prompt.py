"""Unit tests for the generate python code prompt class"""
import sys

import pandas as pd
import pytest

from pandasai.helpers.output_types import (
    output_type_factory,
    DefaultOutputType,
    output_types_map,
)
from pandasai.prompts import GeneratePythonCodePrompt
from pandasai.helpers.viz_library_types import (
    MatplotlibVizLibraryType,
    viz_lib_map,
    viz_lib_type_factory,
)
from pandasai.connectors import PandasConnector


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

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
    def test_str_with_args(
        self, save_charts_path, output_type_hint, viz_library_type_hint
    ):
        """Test casting of prompt to string and interpolation of context.

        Parameterized for the following cases:
        * `save_charts_path` is "exports/charts", `output_type_hint` is default,
        `viz_library_type_hint` is default
        * `save_charts_path` is "custom/dir/for/charts", `output_type_hint`
            is default, `viz_library_type_hint` is default
        * `save_charts_path` is "exports/charts", `output_type_hint` any of
            possible types in `pandasai.helpers.output_types.output_types_map`,
            `viz_library_type_hint` any of
            possible types in `pandasai.helpers.viz_library_types.viz_library_types_map`
        """

        dfs = [PandasConnector({"original_df": pd.DataFrame({"a": [1], "b": [4]})})]
        prompt = GeneratePythonCodePrompt()
        prompt.set_var("dfs", dfs)
        prompt.set_var("last_message", "Q: Question")
        prompt.set_var("save_charts_path", save_charts_path)
        prompt.set_var("output_type_hint", output_type_hint)
        prompt.set_var("viz_library_type", viz_library_type_hint)
        prompt.set_var("skills", "")

        expected_prompt_content = f"""<dataframe>
dfs[0]:1x2
a,b
1,4
</dataframe>




Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: {output_type_hint}
```

Q: Question
Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.
{viz_library_type_hint}


Generate python code and return full updated code:"""  # noqa E501
        actual_prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            actual_prompt_content = actual_prompt_content.replace("\r\n", "\n")
        assert actual_prompt_content == expected_prompt_content
