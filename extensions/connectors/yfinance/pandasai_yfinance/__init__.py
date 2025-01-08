def load_from_yahoo_finance(connection_info, query):
    import yfinance as yf

    ticker = yf.Ticker(connection_info["ticker"])
    data = ticker.history(period=connection_info.get("period", "1mo"))

    return data.to_csv(index=True)


__all__ = ["load_from_yahoo_finance"]
