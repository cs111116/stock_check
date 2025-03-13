# stocks/api/strategy.py
from .stock_data_fetcher import StockDataFetcher
import time
class FetchStrategy:
    def __init__(self, strategy: StockDataFetcher):
        self._strategy = strategy

    def set_strategy(self, strategy: StockDataFetcher):
        """可以動態切換策略"""
        self._strategy = strategy

    def fetch(self, symbol, max_retries=3, retry_delay=2):
        data = self._strategy.fetch_data(symbol, max_retries,retry_delay)
        time.sleep(1)
        return data
    def fetch_history(self, symbol, start_date):
        data = self._strategy.fetch_history_data(symbol, start_date)
        time.sleep(1)
        """執行歷史股價抓取策略"""
        return data
