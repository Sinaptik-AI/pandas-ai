import os

import pandas as pd

from pandasai.workspace import Workspace

os.environ["PANDASAI_API_KEY"] = "$2a$10$/4x9CVetluLt2Rqns7p7Zut8xLYe****"


employees_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Name": ["John", "Emma", "Liam", "Olivia", "William"],
    "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
}

employees_df = pd.DataFrame(employees_data)

workspace = Workspace("order-table-1709039946080")

workspace.push(employees_df, "employees")

workspace.chat("return number or employees")
