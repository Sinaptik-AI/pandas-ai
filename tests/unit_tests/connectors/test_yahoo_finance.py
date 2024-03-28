from unittest.mock import patch

import pytest
import yfinance as yf

import pandasai.pandas as pd
from pandasai.connectors.yahoo_finance import YahooFinanceConnector


@pytest.fixture
def stock_ticker():
    return "AAPL"


@pytest.fixture
def config():
    return {"where": [["column1", "=", "value1"], ["column2", ">", "value2"]]}


@pytest.fixture
def cache_interval():
    return 600


@pytest.fixture
def yahoo_finance_connector(stock_ticker, config, cache_interval):
    return YahooFinanceConnector(stock_ticker, config, cache_interval)


def test_head(yahoo_finance_connector):
    with patch.object(yf.Ticker, "history") as mock_history:
        mock_history.return_value = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0, 4.0, 5.0],
                "High": [2.0, 3.0, 4.0, 5.0, 6.0],
                "Low": [0.5, 1.5, 2.5, 3.5, 4.5],
                "Close": [1.5, 2.5, 3.5, 4.5, 5.5],
                "Volume": [100, 200, 300, 400, 500],
            }
        )
        expected_result = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0, 4.0, 5.0],
                "High": [2.0, 3.0, 4.0, 5.0, 6.0],
                "Low": [0.5, 1.5, 2.5, 3.5, 4.5],
                "Close": [1.5, 2.5, 3.5, 4.5, 5.5],
                "Volume": [100, 200, 300, 400, 500],
            }
        )
        assert yahoo_finance_connector.head().equals(expected_result)


def test_get_cache_path(yahoo_finance_connector):
    with patch("os.path.join") as mock_join:
        expected_result = "../AAPL_data.parquet"
        mock_join.return_value = expected_result
        assert yahoo_finance_connector._get_cache_path() == expected_result


def test_rows_count(yahoo_finance_connector):
    with patch.object(yf.Ticker, "history") as mock_history:
        mock_history.return_value = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0, 4.0, 5.0],
                "High": [2.0, 3.0, 4.0, 5.0, 6.0],
                "Low": [0.5, 1.5, 2.5, 3.5, 4.5],
                "Close": [1.5, 2.5, 3.5, 4.5, 5.5],
                "Volume": [100, 200, 300, 400, 500],
            }
        )
        assert yahoo_finance_connector.rows_count == 5


def test_columns_count(yahoo_finance_connector):
    with patch.object(yf.Ticker, "history") as mock_history:
        mock_history.return_value = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0, 4.0, 5.0],
                "High": [2.0, 3.0, 4.0, 5.0, 6.0],
                "Low": [0.5, 1.5, 2.5, 3.5, 4.5],
                "Close": [1.5, 2.5, 3.5, 4.5, 5.5],
                "Volume": [100, 200, 300, 400, 500],
            }
        )
        assert yahoo_finance_connector.columns_count == 5


def test_fallback_name(yahoo_finance_connector, stock_ticker):
    assert yahoo_finance_connector.fallback_name == stock_ticker
