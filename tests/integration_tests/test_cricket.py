import unittest

import pandasai.pandas as pd
from pandasai.agent.base import Agent
from pandasai.llm import OpenAI

from . import PATH_DATA


class TestCricket(unittest.TestCase):
    def setUp(self) -> None:
        # export OPENAI_API_KEY='sk-...'
        llm = OpenAI(temperature=0)

        csv_file_path = f"{PATH_DATA}/cricket data.csv"

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        self.df = Agent([df], config={"llm": llm})

    def test_number_response(self):
        response = self.df.chat(
            "How many time team won the toss and won the match as well", "number"
        )
        self.assertEqual(response, 11)

    def test_plot_response(self):
        response = self.df.chat(
            "plot histogram of man of match versus number of time man of match", "plot"
        )
        self.assertTrue(
            response.lower().find("pandas-ai/exports/charts/temp_chart.png") != -1
        )
        self.assertTrue(self.df.last_code_generated.find("plot(kind='bar')") != -1)

    def test_string_response(self):
        response = self.df.chat("man of match in final")
        self.assertTrue(response.lower().find("dp conway") != -1)

    def test_dataframe_response(self):
        response = self.df.chat(
            "provide date, match number when team won the toss and won the match as well ordered by match number"
        )
        self.assertTrue(response.head_csv.find("date,match number") != -1)
        self.assertTrue(response.head_csv.find("04-04-2023,7") != -1)
        self.assertTrue(response.head_csv.find("31-03-2023,1") != -1)
        self.assertTrue(response.head_csv.find("02-04-2023,5") != -1)
