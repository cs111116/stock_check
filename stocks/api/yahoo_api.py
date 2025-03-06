import yfinance as yf
import logging

def fetch_stock_data(symbol, period="6mo"):
    """從 Yahoo Finance 獲取股票歷史數據"""
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period=period)
        if history.empty:
            raise ValueError(f"Cannot fetch data for symbol: {symbol}")
        logging.info(f"Data fetched for {symbol} from Yahoo Finance.")
        return history
    except Exception as e:
        logging.error(f"Error fetching data for {symbol} from Yahoo Finance: {e}")
        return None
