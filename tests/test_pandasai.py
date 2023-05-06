"""Unit tests for the PandasAI class"""

from typing import Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandasai import PandasAI
from pandasai.exceptions import LLMNotFoundError
from pandasai.llm.fake import FakeLLM


class TestPandasAI:
    """Unit tests for the PandasAI class"""

    # pylint: disable=missing-function-docstring protected-access invalid-name

    llm: FakeLLM
    pandasai: PandasAI

    def setup(self, output: Optional[str] = None):
        self.llm = FakeLLM(output=output)
        self.pandasai = PandasAI(self.llm)

    def test_init(self):
        self.setup()
        assert self.pandasai._llm == self.llm
        assert self.pandasai._is_conversational_answer is True
        assert self.pandasai._verbose is False

    def test_init_with_llm(self):
        self.setup()
        assert self.pandasai._llm == self.llm
        assert self.pandasai._is_conversational_answer is True
        assert self.pandasai._verbose is False

    def test_init_without_llm(self):
        with pytest.raises(LLMNotFoundError):
            PandasAI()

    def test_conversational_answer(self):
        result = "2"
        self.setup(result)
        assert (
            self.pandasai.conversational_answer("What is the sum of 1 + 1?", "1 + 1", 2)
            == result
        )

    def test_run(self):
        df = pd.DataFrame()
        self.setup(output="1")
        assert self.pandasai.run(df, "What number comes before 2?") == "1"

    def test_run_with_conversational_answer(self):
        df = pd.DataFrame()
        self.setup(output="1 + 1")
        assert (
            self.pandasai.run(
                df, "What is the sum of 1 + 1?", is_conversational_answer=True
            )
            == "1 + 1"
        )

    def test_run_with_non_conversational_answer(self):
        df = pd.DataFrame()
        self.setup(output="1 + 1")
        assert (
            self.pandasai.run(
                df, "What is the sum of 1 + 1?", is_conversational_answer=False
            )
            == 2
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
        assert self.pandasai.run_code("1 + 1", df) == 2

    def test_run_code_invalid_code(self):
        df = pd.DataFrame()
        self.setup()
        with pytest.raises(Exception):
            self.pandasai.run_code("1 +", df)

    def test_run_code_with_print(self):
        df = pd.DataFrame()
        self.setup()
        assert self.pandasai.run_code("print(1 + 1)", df) == 2

    def test_conversational_answer_with_privacy_enforcement(self):
        self.setup()
        self.pandasai._enforce_privacy = True
        self.pandasai._llm.call = Mock(return_value="The answer is 2")
        assert (
            self.pandasai.conversational_answer("How much does 1 + 1 do?", "", 2) == 2
        )
        self.pandasai._llm.call.assert_not_called()

    def test_conversational_answer_without_privacy_enforcement(self):
        self.setup()
        self.pandasai._enforce_privacy = False
        self.pandasai._llm.call = Mock(return_value="The answer is 2")
        assert (
            self.pandasai.conversational_answer("How much does 1 + 1 do?", "", 2)
            == "The answer is 2"
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
        
    def test_run_with_anonymized_df(self):
        df = pd.DataFrame({
            "Phone Number": [
                "(743) 226-2382",
                "+1 123456789",
                "0002223334"
            ],
            "Email": [
                "linda55@nguyen-williams.info",
                "oliverdouglas@lee-harris.biz",
                "sara41@mitchell-rodriguez.com",
            ],
            "Name": [
                "Rachel Davis",
                "Nathan Richards",
                "Monica Scott",
            ],
            "Age": [
                54,
                21,
                27,
            ],
            "Credit Card Number": [
                '5416931670890256',
                '3109-2849-2297-7926',
                '4795 0612 5882 4558',
            ]
        })
        self.setup()
        self.pandasai._is_conversational_answer = True

        expected_non_anonymized_data_frame_substring = """
This is the result of `print(df.head(5))`:
     Phone Number                          Email             Name  Age   Credit Card Number
0  (743) 226-2382   linda55@nguyen-williams.info     Rachel Davis   54     5416931670890256
1    +1 123456789   oliverdouglas@lee-harris.biz  Nathan Richards   21  3109-2849-2297-7926
2      0002223334  sara41@mitchell-rodriguez.com     Monica Scott   27  4795 0612 5882 4558.
"""
        self.pandasai.run(df, "How many people are in the dataframe?", anonymize_df=True)
        self.assertNotIn(expected_non_anonymized_data_frame_substring, self.pandasai._llm.last_prompt)

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
        self.pandasai.run(df, "How many countries are in the dataframe?", anonymize_df = False)
        assert self.pandasai._llm.last_prompt == expected_prompt

    def test_run_with_print_at_the_end(self):
        code = """
result = {"happiness": 0.5, "gdp": 0.8}
print(result)"""
        self.setup(code)
        self.pandasai.run_code(code, pd.DataFrame())

    def test_extract_code(self):
        self.setup()

        code = """```python
result = {"happiness": 0.5, "gdp": 0.8}
print(result)```"""
        assert (
            self.pandasai._llm._extract_code(code)
            == 'result = {"happiness": 0.5, "gdp": 0.8}\nprint(result)'
        )

        code = """```
result = {"happiness": 1, "gdp": 0.43}```"""
        assert (
            self.pandasai._llm._extract_code(code)
            == 'result = {"happiness": 1, "gdp": 0.43}'
        )

        code = """```python<startCode>
result = {"happiness": 0.3, "gdp": 5.5}<endCode>```"""
        assert (
            self.pandasai._llm._extract_code(code)
            == 'result = {"happiness": 0.3, "gdp": 5.5}'
        )

        code = """<startCode>```python
result = {"happiness": 0.49, "gdp": 25.5}```<endCode>"""
        assert (
            self.pandasai._llm._extract_code(code)
            == 'result = {"happiness": 0.49, "gdp": 25.5}'
        )
