# stocks/api/strategy.py
from .stock_data_fetcher import StockDataFetcher

class FetchStrategy:
    def __init__(self, strategy: StockDataFetcher):
        self._strategy = strategy

    def set_strategy(self, strategy: StockDataFetcher):
        """可以動態切換策略"""
        self._strategy = strategy

    def fetch(self, symbol):
        """執行抓取策略"""
        return self._strategy.fetch_data(symbol)
    def fetch_history(self, symbol, start_date):
        """執行歷史股價抓取策略"""
        return self._strategy.fetch_history_data(symbol, start_date)
