import os
import unittest

from pandasai import SmartDataframe
from pandasai.llm import AzureOpenAI, OpenAI

from . import PATH_DATA


class TestGin(unittest.TestCase):
    def setUp(self) -> None:
        # export OPENAI_API_KEY='sk-...'
        llm = OpenAI(temperature=0)
        self.df = SmartDataframe(f"{PATH_DATA}/Gins_List.csv", config={"llm": llm})

    def test_number_response(self):
        response = self.df.chat("Average price of Gin rounded off", "number")
        self.assertEqual(response, 57.15)

    def test_plot_response(self):
        response = self.df.chat("Plot note versus number of Gins with the note")
        self.assertTrue(
            response.lower().find("pandas-ai/exports/charts/temp_chart.png") != -1
        )

    def test_string_response(self):
        response = self.df.chat("Name the costliest gin")
        self.assertTrue(response.find("Robert Burnett\nOld Tom Gin Bot.1940s.") != -1)

    def test_dataframe_response(self):
        response = self.df.chat(
            "provide name, country and price gins with most number of reviews"
        )
        self.assertTrue(response.head_csv.find("name,country,Number of reviews") != -1)
        self.assertTrue(
            response.head_csv.find("Drumshanbo Gunpowder I...,Ireland,51.0") != -1
        )
        self.assertTrue(
            response.head_csv.find("Xoriguer Mahon Gin...,Spain,56.0") != -1
        )
        self.assertTrue(
            response.head_csv.find("Monkey 47 Schwarzwald ...,Germany,57.0") != -1
        )
