import unittest

import pandasai.pandas as pd
from pandasai.agent.base import Agent
from pandasai.llm import OpenAI

from . import PATH_DATA


class TestNewYorkHousing(unittest.TestCase):
    def setUp(self) -> None:
        # export OPENAI_API_KEY='sk-...'
        llm = OpenAI(temperature=0)

        csv_file_path = f"{PATH_DATA}/NY-House-Dataset.csv"

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        self.df = Agent([df], config={"llm": llm})

    def test_number_response(self):
        response = self.df.chat("Average price of Condo for sale", "number")
        self.assertEqual(response, 2630710)

    def test_plot_response(self):
        response = self.df.chat("plot type versus avergae price of type")
        self.assertTrue(
            response.lower().find("pandas-ai/exports/charts/temp_chart.png") != -1
        )

    def test_string_response(self):
        response = self.df.chat("address of cheapest property")
        self.assertEqual(response, "635 W 170th St Apt 4F")

    def test_dataframe_response(self):
        response = self.df.chat(
            "brokertitle, type, price of cheapest properties", "dataframe"
        )
        self.assertTrue(response.head_csv.find("BROKERTITLE,TYPE,PRICE") != -1)
        self.assertTrue(
            response.head_csv.find("Brokered by Century 21...,Land for sale,5800") != -1
        )
        self.assertTrue(
            response.head_csv.find("Brokered by Living NY ...,For sale,3225") != -1
        )
        self.assertTrue(
            response.head_csv.find("Brokered by Living NY ...,For sale,2494") != -1
        )
