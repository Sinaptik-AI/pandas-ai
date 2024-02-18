"""
Example of using displaying PandasAI charts in Flask

Usage:
flask –-app using_flask.py run
"""
import pandas as pd
from flask import Flask, render_template, request

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser

app = Flask(__name__)


# This class overrides default behaviour how dataframe is returned
# By Default PandasAI returns the SmartDataFrame
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


@app.route("/pandasai", methods=["GET", "POST"])
def pandasai():
    if request.method == "POST":
        # prompt question such as "Return a dataframe of name against salaries"
        query = request.form["query"]
        response = dl.chat(query)

        # Returns the response as Pandas DataFrame object in html
        return render_template("sample_flask_salaries.html", response=response)

    return render_template("sample_flask_salaries.html")


if __name__ == "__main__":
    app.run()
