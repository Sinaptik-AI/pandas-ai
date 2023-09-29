"""
Example of using displaying PandasAI charts in Streamlit

Usage:
streamlit run examples/using_streamlit.py
"""
import pandas as pd

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.responses.streamlit_response import StreamlitResponse


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
    config={"llm": llm, "verbose": True, "response_parser": StreamlitResponse},
)

dl.chat("Plot salaries against employee name")
