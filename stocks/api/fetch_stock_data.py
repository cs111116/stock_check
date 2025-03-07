# api/fetch_stock_data.py
from .fetcher import YahooFinanceFetcher
from .scraper import WebScraperFetcher
from .strategy import FetchStrategy
from .twsefetcher import TwseFetcher  # 匯入歷史股價抓取器
import pdb
def fetch_stock_data(symbol):
    """統一的資料抓取邏輯，根據資料類型抓取即時或歷史股價"""
    # 即時股價抓取
    yf_fetcher = YahooFinanceFetcher()
    strategy = FetchStrategy(yf_fetcher)
    data = strategy.fetch(symbol)
    if data is None or not is_valid_data(data):
        print(f"Falling back to scraping for {symbol}...")
        scraper_fetcher = WebScraperFetcher()
        strategy.set_strategy(scraper_fetcher)  # 切換爬蟲策略
        data = strategy.fetch(symbol)
    if data is None or not is_valid_data(data):
        print(f"Failed to fetch valid real-time data for {symbol}.")
        return None
    return data
def fetch_history(symbol, start_date):
    # 歷史股價抓取
    # 使用 TwseFetcher 來抓取歷史股價資料
    twse_fetcher = TwseFetcher()
    strategy = FetchStrategy(twse_fetcher)
    data = strategy.fetch_history(symbol,start_date)
    pdb.set_trace()
    if data is None:
        print(f"Failed to fetch valid historical data for {symbol}.")
        return None
    return data
def is_valid_data(data):
    """檢查資料是否有效"""
    required_fields = ['Current Price', 'Previous Close', 'Open Price', 'High Price', 'Low Price', 'Volume']
    # 檢查每個必須的欄位是否存在且不是空
    for field in required_fields:
        if field not in data or data[field] is None or (hasattr(data[field], 'empty') and data[field].empty):
            print(f"Missing or invalid value for {field}")
            return False
    return True
