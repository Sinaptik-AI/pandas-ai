import unittest
from pandasai import SmartDataframe
from pandasai.llm import OpenAI


class TestLoadPayments(unittest.TestCase):
    def setUp(self) -> None:
        llm = OpenAI("open-ai-key")
        self.df = SmartDataframe(
            "examples/data/Loan payments data.csv", config={"llm": llm}
        )

    def test_number_response(self):
        response = self.df.chat(
            "How many loans are from men and have been paid off?", "number"
        )
        self.assertEqual(response, 247)

    def test_plot_response(self):
        self.df.chat("Plot of age against loan_status ")
        # self.assertEqual(response, )

    def test_string_response(self):
        response = self.df.chat(
            "Will women with education high school of below will pay off loan on time?"
        )
        self.assertTrue(response.lower().find("true") != -1)

    def test_dataframe_response(self):
        response = self.df.chat(
            "Load ID and pricipal of paidoff loan ordered by Loan ID", "dataframe"
        )
        self.assertTrue(response.head_csv.find("Loan_ID,Principal") != -1)
        self.assertTrue(response.head_csv.find("xqd20160003,1000") != -1)
        self.assertTrue(response.head_csv.find("xqd12160159,1000") != -1)
        self.assertTrue(response.head_csv.find("xqd20160004,1000") != -1)
