"""Unit tests for the correct error prompt class"""
import os
import sys

import pandas as pd
import pytest

from pandasai import Agent
from pandasai.llm.fake import FakeLLM
from pandasai.prompts.generate_python_code_with_sql import (
    GeneratePythonCodeWithSQLPrompt,
)


class TestGeneratePythonCodeWithSQLPrompt:
    """Unit tests for the correct error prompt class"""

    @pytest.mark.parametrize(
        "output_type,output_type_template",
        [
            *[
                (
                    "",
                    """type (possible values "string", "number", "dataframe", "plot"). Examples: { "type": "string", "value": f"The highest salary is {highest_salary}." } or { "type": "number", "value": 125 } or { "type": "dataframe", "value": pd.DataFrame({...}) } or { "type": "plot", "value": "temp_chart.png" }""",
                ),
                (
                    "number",
                    """type (must be "number"), value must int. Example: { "type": "number", "value": 125 }""",
                ),
                (
                    "dataframe",
                    """type (must be "dataframe"), value must be pd.DataFrame or pd.Series. Example: { "type": "dataframe", "value": pd.DataFrame({...}) }""",
                ),
                (
                    "plot",
                    """type (must be "plot"), value must be string. Example: { "type": "plot", "value": "temp_chart.png" }""",
                ),
                (
                    "string",
                    """type (must be "string"), value must be string. Example: { "type": "string", "value": f"The highest salary is {highest_salary}." }""",
                ),
            ]
        ],
    )
    def test_str_with_args(self, output_type, output_type_template):
        """Test that the __str__ method is implemented"""

        os.environ["PANDASAI_API_URL"] = ""
        os.environ["PANDASAI_API_KEY"] = ""

        llm = FakeLLM()
        agent = Agent(pd.DataFrame(), config={"llm": llm})
        prompt = GeneratePythonCodeWithSQLPrompt(
            context=agent.context,
            output_type=output_type,
        )
        prompt_content = prompt.to_string()
        if sys.platform.startswith("win"):
            prompt_content = prompt_content.replace("\r\n", "\n")

        print(prompt_content)

        assert (
            prompt_content
            == f'''<tables>
<table>
dfs[0]:
  name: null
  description: null
  type: pd.DataFrame
  rows: 0
  columns: 0
  schema:
    fields: []

</table>
</tables>


You can call the following functions that have been pre-defined for you:

<function>
def execute_sql_query(sql_query: str) -> pd.Dataframe
    """This method connects to the database, executes the sql query and returns the dataframe"""
</function>


Update this initial code:
```python
# TODO: import the required dependencies
import pandas as pd

# Write code here

# Declare result var: 
{output_type_template}

```




Variable `dfs: list[pd.DataFrame]` is already declared.

At the end, declare "result" variable as a dictionary of type and value.


Generate python code and return full updated code:

### Note: Use only relevant table for query and do aggregation, sorting, joins and grouby through sql query'''  # noqa: E501
        )
