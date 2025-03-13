# api/fetch_stock_data.py
from .fetcher import YahooFinanceFetcher
from .scraper import WebScraperFetcher
from .strategy import FetchStrategy
from .twsefetcher import TwseFetcher  # 匯入歷史股價抓取器
import logging
import time
import pdb
from stocks.log_config import logging_info,logging_error

def fetch_stock_data(symbol):
    """統一的資料抓取邏輯，根據資料類型抓取即時股價"""
    # 即時股價抓取
    yf_fetcher = YahooFinanceFetcher()
    strategy = FetchStrategy(yf_fetcher)
    logging_info(f"使用YahooFinanceFetcher API {symbol}")
    data = strategy.fetch(symbol, max_retries=3, retry_delay=2)
    if data is None or not is_valid_data(data):
        logging_info(f"YahooFinanceFetcher API失敗... {symbol}:{data}")
        logging_info(f"使用YAHOO網站爬蟲 {symbol}")
        scraper_fetcher = WebScraperFetcher()
        strategy.set_strategy(scraper_fetcher)  # 切換爬蟲策略
        data = strategy.fetch(symbol, max_retries=3, retry_delay=2)
        if data is None or not is_valid_data(data):
            logging_info(f"YahooFinanceFetcher API&爬蟲失敗 {symbol}.")
            return None
    logging_info(f"{symbol} 成功獲取")
    return data
def fetch_history(symbol, start_date=None):
    # 歷史股價抓取
    yf_fetcher = YahooFinanceFetcher()
    strategy = FetchStrategy(yf_fetcher)
    logging_info(f"使用YahooFinanceFetcher API {symbol}")
    data = strategy.fetch_history(symbol, start_date)
    if data is None:
        logging_info(f"YahooFinanceFetcher API失敗... {symbol}:{data}")
        logging_info(f"使用TWSE網站爬蟲 {symbol}")
        twse_fetcher = TwseFetcher()
        strategy = FetchStrategy(twse_fetcher)
        data = strategy.fetch_history(symbol,start_date)
        if data is None:
            logging_error(f"抓歷史紀錄失敗 {symbol}.")
            return None
    logging_info(f"{symbol} 成功獲取")
    return data
def is_valid_data(data):
    """檢查資料是否有效"""
    required_fields = ['Current_Price', 'Previous_Price', 'Open', 'High', 'Low', 'Volume']
    # 檢查每個必須的欄位是否存在且不是空
    for field in required_fields:
        if field not in data or data[field] is None or (hasattr(data[field], 'empty') and data[field].empty):
            logging.error(f"缺少參數為 {field}, 當前資料: {data}")
            return False
    return True