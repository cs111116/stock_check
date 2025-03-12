# stocks/api/fetcher.py
from .stock_data_fetcher import StockDataFetcher
import yfinance as yf
import pandas as pd
from stocks.log_config import logging_info,logging_error
import pdb
from stocks.models import StockInfo
class YahooFinanceFetcher(StockDataFetcher):
    """從 Yahoo Finance 抓取資料的具體實現"""
    def fetch_data(self, symbol, max_retries,retry_delay):
        """從 Yahoo Finance 抓取股票資料"""
        if symbol.isdigit():  # 判斷是否為數字，為台股
            symbol = f"{symbol}.TW"
        elif symbol.isalpha() and symbol.isupper():  # 判斷是否為大寫字母，為美股
            symbol = f"{symbol}"
        else:
            logging_error(f"無效的股票代號：{symbol}")
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
                    'Current_Price': [round(todayDate['Close'],2)],
                    'Previous_Close': [round(previousDate["Close"],2)],
                    'Open_Price': [round(todayDate["Open"],2)],
                    'High_Price': [ round(todayDate["High"],2)],
                    'Low_Price': [round(todayDate["Low"],2)],
                    'Volume': [ todayDate["Volume"]]
                }
            else:
                logging_error(f"回傳資料失敗 : {history}")
                return None
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            logging_error(f"YF_API發生意外錯誤 {symbol}: {e}")
            return None
    def fetch_history_data(self, symbol, start_date="6mo"):
        if symbol.isdigit():  # 判斷是否為數字，為台股
            # 根據資料庫查詢股票資料
            stock_info = StockInfo.objects.filter(stock_code=symbol).first()
            if stock_info:
                if stock_info.market_type == 1:  # 上市
                    if stock_info.security_type == 2:  # ETF
                        symbol = f"{symbol}.TWO"  # 上市 ETF 代號加上 .TWO
                    else:
                        symbol = f"{symbol}.TW"  # 上市股票代號加上 .TW
                elif stock_info.market_type == 2:  # 上櫃
                    symbol = f"{symbol}.TWO"  # 上櫃股票代號加上 .TWO
        else:
            logging_error(f"無效的股票代號：{symbol}")
            return None
        """從 Yahoo Finance 抓取歷史股價資料"""
        pdb.set_trace()
        stock = yf.Ticker(symbol)
        history = stock.history("6mo")  # Fetch history from start_date
        if len(history) > 0:
            return history
        return None