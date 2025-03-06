import requests
import logging

def fetch_stock_data(symbol, period="6mo"):
    """從 Alpha Vantage 獲取股票歷史數據"""
    try:
        api_key = "YOUR_ALPHA_VANTAGE_API_KEY"
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full"
        response = requests.get(url)
        data = response.json()

        if "Time Series (Daily)" not in data:
            raise ValueError(f"Cannot fetch data for symbol: {symbol}")
        logging.info(f"Data fetched for {symbol} from Alpha Vantage.")
        return data["Time Series (Daily)"]
    except Exception as e:
        logging.error(f"Error fetching data for {symbol} from Alpha Vantage: {e}")
        return None
