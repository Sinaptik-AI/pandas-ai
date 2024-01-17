import os
import unittest
from pandasai import SmartDataframe
from pandasai.llm import OpenAI


class TestNewYorkHousing(unittest.TestCase):
    def setUp(self) -> None:
        llm = OpenAI(os.environ.get("API_KEY"))
        self.df = SmartDataframe(
            "integration/NY-House-Dataset.csv", config={"llm": llm}
        )

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
