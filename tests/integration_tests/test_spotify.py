import os
import unittest

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from . import PATH_DATA


class TestSpotify(unittest.TestCase):
    def setUp(self) -> None:
        # export OPENAI_API_KEY='sk-...'
        llm = OpenAI(temperature=0)
        self.df = SmartDataframe(f"{PATH_DATA}/artists.csv", config={"llm": llm})

    def test_number_response(self):
        response = self.df.chat("streams of Imagine Dragons", "number")
        self.assertEqual(response, 28100)

    def test_plot_response(self):
        response = self.df.chat("Plot data of top 5 streamed artists")
        self.assertTrue(
            response.lower().find("pandas-ai/exports/charts/temp_chart.png") != -1
        )

    def test_string_response(self):
        response = self.df.chat("Name the highest streamed artist")
        self.assertTrue(response.find("Drake") != -1)

    def test_dataframe_response(self):
        response = self.df.chat("top 3 daily artists and daily stream data")
        self.assertTrue(response.head_csv.find("Artist,Daily") != -1)
        self.assertTrue(response.head_csv.find("Drake,50.775") != -1)
        self.assertTrue(response.head_csv.find("Olivia Rodrigo,71.896") != -1)
        self.assertTrue(response.head_csv.find("Taylor Swift,85.793") != -1)
