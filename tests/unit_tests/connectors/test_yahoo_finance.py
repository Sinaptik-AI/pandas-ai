from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest
import yfinance as yf

from extensions.connectors.yfinance.pandasai_yfinance.yahoo_finance import YahooFinanceConnector
from extensions.connectors.yfinance.pandasai_yfinance import load_from_yahoo_finance


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
        
def test_load_from_yahoo_finance_default_period():
    # Arrange
    connection_info = {"ticker": "AAPL"}
    mock_ticker = Mock()
    mock_history = pd.DataFrame({"Close": [100, 101, 102]})
    mock_ticker.history.return_value = mock_history

    # Act
    with patch("yfinance.Ticker", return_value=mock_ticker) as mock_yf_ticker:
        result = load_from_yahoo_finance(connection_info, None)

    # Assert
    mock_yf_ticker.assert_called_once_with("AAPL")
    mock_ticker.history.assert_called_once_with(period="1mo")
    assert isinstance(result, str)
    assert "Close" in result
    assert "100" in result and "101" in result and "102" in result

def test_load_from_yahoo_finance_custom_period():
    # Arrange
    connection_info = {"ticker": "GOOGL", "period": "3mo"}
    mock_ticker = Mock()
    mock_history = pd.DataFrame({"Close": [200, 201, 202]})
    mock_ticker.history.return_value = mock_history

    # Act
    with patch("yfinance.Ticker", return_value=mock_ticker) as mock_yf_ticker:
        result = load_from_yahoo_finance(connection_info, None)

    # Assert
    mock_yf_ticker.assert_called_once_with("GOOGL")
    mock_ticker.history.assert_called_once_with(period="3mo")
    assert isinstance(result, str)
    assert "Close" in result
    assert "200" in result and "201" in result and "202" in result

def test_load_from_yahoo_finance_query_ignored():
    # Arrange
    connection_info = {"ticker": "MSFT"}
    query = "This query should be ignored"
    mock_ticker = Mock()
    mock_history = pd.DataFrame({"Close": [300, 301, 302]})
    mock_ticker.history.return_value = mock_history

    # Act
    with patch("yfinance.Ticker", return_value=mock_ticker) as mock_yf_ticker:
        result = load_from_yahoo_finance(connection_info, query)

    # Assert
    mock_yf_ticker.assert_called_once_with("MSFT")
    mock_ticker.history.assert_called_once_with(period="1mo")
    assert isinstance(result, str)
    assert "Close" in result
    assert "300" in result and "301" in result and "302" in result
