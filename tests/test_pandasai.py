"""Unit tests for the PandasAI class"""

import unittest
from unittest.mock import patch, Mock

import pandas as pd
from pandasai import PandasAI
from pandasai.llm.fake import FakeLLM
from pandasai.exceptions import LLMNotFoundError


class TestPandasAI(unittest.TestCase):
    """Unit tests for the PandasAI class"""

    llm: FakeLLM
    pandasai: PandasAI

    def setup(self, output: str = None):
        self.llm = FakeLLM(output=output)
        self.pandasai = PandasAI(self.llm)

    def test_init(self):
        self.setup()
        self.assertEqual(self.pandasai._llm, self.llm)
        self.assertEqual(self.pandasai._is_conversational_answer, True)
        self.assertEqual(self.pandasai._verbose, False)

    def test_init_with_llm(self):
        self.setup()
        self.assertEqual(self.pandasai._llm, self.llm)
        self.assertEqual(self.pandasai._is_conversational_answer, True)
        self.assertEqual(self.pandasai._verbose, False)

    def test_init_without_llm(self):
        with self.assertRaises(LLMNotFoundError):
            PandasAI()

    def test_conversational_answer(self):
        result = "2"
        self.setup(result)
        self.assertEqual(
            self.pandasai.conversational_answer(
                "What is the sum of 1 + 1?", "1 + 1", 2
            ),
            result,
        )

    def test_run(self):
        df = pd.DataFrame()
        self.setup(output="1")
        self.assertEqual(self.pandasai.run(df, "What number comes before 2?"), "1")

    def test_run_with_conversational_answer(self):
        df = pd.DataFrame()
        self.setup(output="1 + 1")
        self.assertEqual(
            self.pandasai.run(
                df, "What is the sum of 1 + 1?", is_conversational_answer=True
            ),
            "1 + 1",
        )

    def test_run_with_non_conversational_answer(self):
        df = pd.DataFrame()
        self.setup(output="1 + 1")
        self.assertEqual(
            self.pandasai.run(
                df, "What is the sum of 1 + 1?", is_conversational_answer=False
            ),
            2,
        )

    def test_run_with_verbose(self):
        df = pd.DataFrame()
        self.setup(output="1")
        self.pandasai._verbose = True

        # mock print function
        with patch("builtins.print") as mock_print:
            self.pandasai.run(df, "What number comes before 2?")
            mock_print.assert_called()

    def test_run_without_verbose(self):
        df = pd.DataFrame()
        self.setup(output="1")
        self.pandasai._verbose = False

        # mock print function
        with patch("builtins.print") as mock_print:
            self.pandasai.run(df, "What number comes before 2?")
            mock_print.assert_not_called()

    def test_run_code(self):
        df = pd.DataFrame()
        self.setup()
        self.assertEqual(self.pandasai.run_code("1 + 1", df), 2)

    def test_run_code_invalid_code(self):
        df = pd.DataFrame()
        self.setup()
        with self.assertRaises(Exception):
            self.pandasai.run_code("1 +", df)

    def test_run_code_with_print(self):
        df = pd.DataFrame()
        self.setup()
        self.assertEqual(self.pandasai.run_code("print(1 + 1)", df), 2)

    def test_conversational_answer_with_privacy_enforcement(self):
        self.setup()
        self.pandasai._enforce_privacy = True
        self.pandasai._llm.call = Mock(return_value="The answer is 2")
        self.assertEqual(
            self.pandasai.conversational_answer("How much does 1 + 1 do?", "", 2), 2
        )
        self.pandasai._llm.call.assert_not_called()

    def test_conversational_answer_without_privacy_enforcement(self):
        self.setup()
        self.pandasai._enforce_privacy = False
        self.pandasai._llm.call = Mock(return_value="The answer is 2")
        self.assertEqual(
            self.pandasai.conversational_answer("How much does 1 + 1 do?", "", 2),
            "The answer is 2",
        )
        self.pandasai._llm.call.assert_called()

    def test_run_with_privacy_enforcement(self):
        df = pd.DataFrame({"country": ["United States", "United Kingdom", "France"]})
        self.setup()
        self.pandasai._enforce_privacy = True
        self.pandasai._is_conversational_answer = True

        expected_prompt = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.head(0))`:
Empty DataFrame
Columns: [country]
Index: [].

Return the python code (do not import anything) and make sure to prefix the python code with <startCode> exactly and suffix the code with <endCode> exactly 
to get the answer to the following question :
How many countries are in the dataframe?"""
        self.pandasai.run(df, "How many countries are in the dataframe?")
        assert self.pandasai._llm.last_prompt == expected_prompt

    def test_run_without_privacy_enforcement(self):
        df = pd.DataFrame({"country": ["United States", "United Kingdom", "France"]})
        self.setup()
        self.pandasai._enforce_privacy = False
        self.pandasai._is_conversational_answer = False

        expected_prompt = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.head(5))`:
          country
0   United States
1  United Kingdom
2          France.

Return the python code (do not import anything) and make sure to prefix the python code with <startCode> exactly and suffix the code with <endCode> exactly 
to get the answer to the following question :
How many countries are in the dataframe?"""
        self.pandasai.run(df, "How many countries are in the dataframe?")
        assert self.pandasai._llm.last_prompt == expected_prompt