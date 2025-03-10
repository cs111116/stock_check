# stocks/api/stock_data_fetcher.py
from abc import ABC, abstractmethod

class StockDataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, symbol):
        """ 抓取股票資料的方法 """
        pass
    def fetch_history_data(self, symbol, start_date=None):
        """ 抓取歷史股價資料 """
        pass