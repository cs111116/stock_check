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
            # 根據資料庫查詢股票資料
            stock_info = StockInfo.objects.filter(stock_code=symbol).first()
            if stock_info:
                if stock_info.market_type == 1:  # 上市
                    symbol = f"{symbol}.TW"  # 上市股票代號加上 .TW
                elif stock_info.market_type == 2:  # 上櫃
                    symbol = f"{symbol}.TWO"  # 上櫃股票代號加上 .TWO
        else:
            logging_error(f"無效的股票代號：{symbol}")
            return None
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            data = {
                'Date': pd.to_datetime('today'),
                'Current_Price': round(info['regularMarketPrice'], 2),  # 當前市場價格
                'Previous_Price': round(info['previousClose'], 2),  # 前一日收盤價
                'Open': round(info['regularMarketOpen'], 2),  # 當日開盤價
                'High': round(info['regularMarketDayHigh'], 2),  # 當日最高價
                'Low': round(info['regularMarketDayLow'], 2),  # 當日最低價
                'Volume': info['regularMarketVolume'],  # 當日交易量
            }
            dividendYield = f"{round(info['dividendYield'], 2)}%"
            if 'dividendRate' in info and info['dividendYield'] is not None:
                data['Yield'] = dividendYield #宣告殖利率
                data['Forward_dividend_yield'] = None #目前殖利率
            else:
                data['Yield'] = None
                data['Forward_dividend_yield'] = dividendYield
            return data
        except Exception as e:
            logging_error(f"YF_API發生意外錯誤 {symbol}: {e}")
            return None
    def fetch_history_data(self, symbol, start_date):
        # 根據資料庫查詢股票資料
        stock_info = StockInfo.objects.filter(stock_code=symbol).first()
        if stock_info:
            if stock_info.market_type == 1:  # 上市
                    symbol = f"{symbol}.TW"  # 上市股票代號加上 .TW
            elif stock_info.market_type == 2:  # 上櫃
                symbol = f"{symbol}.TWO"  # 上櫃股票代號加上 .TWO
        else:
            logging_error(f"沒有此股票代號 請更新股票資訊：{symbol}")
            return None
        if start_date is None:
            start_date = "6mo"
        """從 Yahoo Finance 抓取歷史股價資料"""
        stock = yf.Ticker(symbol)
        history = stock.history(start_date)  # Fetch history from start_date
        if len(history) > 0:
            return history
        return None