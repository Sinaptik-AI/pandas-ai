# Streamlit

PandasAI offers the flexibility to handle chat responses in a customized manner. By default, PandasAI includes a ResponseParser class that can be extended to modify the response output according to your needs.

You have the option to provide a custom parser, such as `StreamLitResponse`, to the configuration object like this:

## Example Usage

```python

import pandas as pd

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.response.streamlit_response import StreamLitResponse


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

llm = OpenAI()
dl = SmartDatalake(
    [employees_df, salaries_df],
    config={"llm": llm, "verbose": True, "response_parser": StreamLitResponse},
)

dl.chat("Plot salaries against name")

```
