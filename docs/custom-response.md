# Custom Response

PandasAI offers the flexibility to handle chat responses in a customized manner. By default, PandasAI includes a ResponseParser class that can be extended to modify the response output according to your needs.

You have the option to provide a custom parser, such as `StreamLitResponse`, to the configuration object like this:

## Example Usage

```python

import pandas as pd

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.response.response_parser import ResponseParser

# This class overrides default behaviour how dataframe is returned
# By Default PandasAi returns the SmartDataFrame
class PandasDataFrame(ResponseParser):

    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        # Returns Pandas Dataframe instead of SmartDataFrame
        return result["value"]


employees_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Name": ["John", "Emma", "Liam", "Olivia", "William"],
        "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
    }
)

salaries_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Salary": [5000, 6000, 4500, 7000, 5500],
    }
)

llm = OpenAI("OPENAI-KEY")
dl = SmartDatalake(
    [employees_df, salaries_df],
    config={"llm": llm, "verbose": True, "response_parser": PandasDataFrame},
)

response = dl.chat("Return a dataframe of name against salaries")
# Returns the response as Pandas DataFrame

```
