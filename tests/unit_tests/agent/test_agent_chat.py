import os
from typing import List, Tuple

import pytest

import pandasai as pai
from pandasai import DataFrame
from pandasai.core.response import NumberResponse

# Read the API key from an environment variable
API_KEY = os.getenv("PANDASAI_API_KEY_TEST_CHAT", None)


class TestAgentChat:
    @pytest.fixture
    def pandas_ai(self):
        pai.api_key.set(API_KEY)
        return pai

    @pytest.mark.parametrize(
        "question,expected",
        [
            ("What is the total quantity sold across all products and regions?", 105),
            ("What is the correlation coefficient between Sales and Profit?", 1.0),
            (
                "What is the standard deviation of daily sales for the entire dataset?",
                231.0,
            ),
            (
                "Give me the number of the highest average profit margin among all regions?",
                0.2,
            ),
            (
                "What is the difference in total Sales between Product A and Product B across the entire dataset?",
                700,
            ),
            ("Over the entire dataset, how many days had sales above 900?", 5),
            (
                "What was the year-over-year growth in total sales from 2022 to 2023 (in percent)?",
                7.84,
            ),
        ],
    )
    @pytest.mark.integration
    @pytest.mark.skipif(
        API_KEY is None, reason="API key not set, skipping integration tests"
    )
    def test_integration_multiple_numeric_questions(
        self, question, expected, pandas_ai
    ):
        """
        A single integration test that checks 10 numeric questions on a DataFrame
        aligned with real-world data analysis scenarios.
        """

        # Sample DataFrame spanning two years (2022-2023), multiple regions and products
        df = DataFrame(
            {
                "Date": [
                    "2022-01-01",
                    "2022-01-02",
                    "2022-01-03",
                    "2022-02-01",
                    "2022-02-02",
                    "2022-02-03",
                    "2023-01-01",
                    "2023-01-02",
                    "2023-01-03",
                    "2023-02-01",
                    "2023-02-02",
                    "2023-02-03",
                ],
                "Region": [
                    "North",
                    "North",
                    "South",
                    "South",
                    "East",
                    "East",
                    "North",
                    "North",
                    "South",
                    "South",
                    "East",
                    "East",
                ],
                "Product": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
                "Sales": [
                    1000,
                    800,
                    1200,
                    900,
                    500,
                    700,
                    1100,
                    850,
                    1250,
                    950,
                    600,
                    750,
                ],
                "Profit": [200, 160, 240, 180, 100, 140, 220, 170, 250, 190, 120, 150],
                "Quantity": [10, 8, 12, 9, 5, 7, 11, 8, 13, 9, 6, 7],
            }
        )

        response = pandas_ai.chat(question, df)

        assert isinstance(
            response, NumberResponse
        ), f"Expected a NumberResponse, got {type(response)} for question: {question}"

        model_value = float(response.value)

        assert model_value == pytest.approx(expected, abs=0.5), (
            f"Question: {question}\n" f"Expected: {expected}, Got: {model_value}"
        )
