# api/fetch_stock_data.py
from .fetcher import YahooFinanceFetcher
from .scraper import WebScraperFetcher
from .strategy import FetchStrategy
from .twsefetcher import TwseFetcher  # 匯入歷史股價抓取器
import logging
import pdb
from stocks.log_config import logging_info,logging_error

def fetch_stock_data(symbol):
    """統一的資料抓取邏輯，根據資料類型抓取即時或歷史股價"""
    # 即時股價抓取
    yf_fetcher = WebScraperFetcher()
    strategy = FetchStrategy(yf_fetcher)
    data = strategy.fetch(symbol, max_retries=3, retry_delay=2)
    if data is None or not is_valid_data(data):
        logging_info(f"YF_API失敗... {symbol}:{data}")
        scraper_fetcher = WebScraperFetcher()
        strategy.set_strategy(scraper_fetcher)  # 切換爬蟲策略
        data = strategy.fetch(symbol, max_retries=3, retry_delay=2)
    if data is None or not is_valid_data(data):
        logging_info(f"YF_API&爬蟲失敗 {symbol}.")
        return None
    return data
def fetch_history(symbol, start_date=None):
    # 歷史股價抓取
    # 使用 TwseFetcher 來抓取歷史股價資料
    twse_fetcher = TwseFetcher()
    strategy = FetchStrategy(twse_fetcher)
    data = strategy.fetch_history(symbol,start_date)
    if data is None:
        logging_error(f"抓歷史紀錄失敗 {symbol}.")
        return None
    return data
def is_valid_data(data):
    """檢查資料是否有效"""
    required_fields = ['Current_Price', 'Previous_Close', 'Open_Price', 'High_Price', 'Low_Price', 'Volume']
    # 檢查每個必須的欄位是否存在且不是空
    for field in required_fields:
        if field not in data or data[field] is None or (hasattr(data[field], 'empty') and data[field].empty):
            logging.error(f"缺少參數為 {field}")
            return False
    return True
