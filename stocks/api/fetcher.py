# stocks/api/fetcher.py
from .stock_data_fetcher import StockDataFetcher
import yfinance as yf
import pandas as pd

class YahooFinanceFetcher(StockDataFetcher):
    """從 Yahoo Finance 抓取資料的具體實現"""
    def fetch_data(self, symbol):
        """從 Yahoo Finance 抓取股票資料"""
        if symbol.isdigit():  # 判斷是否為數字，為台股
            symbol = f"{symbol}.TW"
        elif symbol.isalpha() and symbol.isupper():  # 判斷是否為大寫字母，為美股
            symbol = f"{symbol}"
        else:
            print(f"無效的股票代號：{symbol}")
            return None
        try:
            stock = yf.Ticker(symbol)
            history = stock.history("2d")
            if len(history) == 2 and not history.iloc[-1].isnull().any() and not history.iloc[-2].isnull().any():
                # 取最新的資料
                todayDate = history.iloc[-1]
                # 取前一天的資料
                previousDate = history.iloc[-2]
                data = {
                    'Date': [pd.to_datetime('today')],
                    'Current Price': [round(todayDate['Close'],2)],
                    'Previous Close': [round(previousDate["Close"],2)],
                    'Open Price': [round(todayDate["Open"],2)],
                    'High Price': [ round(todayDate["High"],2)],
                    'Low Price': [round(todayDate["Low"],2)],
                    'Volume': [ todayDate["Volume"]]
                }
            # 檢查資料是否為空，若為空則視為抓取失敗
            if not data:
                raise ValueError(f"Cannot fetch data for symbol: {symbol} from Yahoo Finance.")
            else:
                df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return None
    # def fetch_history_data(self, symbol, start_date):
    #     """從 Yahoo Finance 抓取歷史股價資料"""
    #     stock = yf.Ticker(symbol)
    #     history = stock.history(start=start_date)  # Fetch history from start_date
    #     if len(history) > 0:
    #         return history[['Close', 'Open', 'High', 'Low', 'Volume']]
    #     return None