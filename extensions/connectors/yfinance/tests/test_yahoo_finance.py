import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

# Assuming the functions are in a module called yahoo_finance
from pandasai_yfinance import load_from_yahoo_finance


class TestYahooFinanceLoader(unittest.TestCase):
    @patch("yfinance.Ticker")
    def test_load_from_yahoo_finance(self, MockTicker):
        # Setup the mock return value for history method
        mock_ticker_instance = MagicMock()
        MockTicker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02"],
                "Open": [150, 152],
                "High": [155, 157],
                "Low": [148, 150],
                "Close": [153, 155],
                "Volume": [100000, 120000],
            },
            index=pd.to_datetime(["2025-01-01", "2025-01-02"]),
        )

        # Test data
        connection_info = {"ticker": "AAPL", "period": "1d"}
        query = (
            ""
        )  # Since the query parameter is not used, we can leave it as an empty string

        # Call the function under test
        result = load_from_yahoo_finance(connection_info, query)

        # Assert that the Ticker method was called with the correct ticker symbol
        MockTicker.assert_called_once_with("AAPL")

        # Assert that the history method was called with the correct period
        mock_ticker_instance.history.assert_called_once_with(period="1d")

        print(result)

        # Assert the result is a CSV string
        self.assertTrue(result.startswith(",Date,Open,High,Low,Close,Volume"))
        self.assertIn("2025-01-01", result)
        self.assertIn("2025-01-02", result)


if __name__ == "__main__":
    unittest.main()
