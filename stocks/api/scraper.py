# api/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from stocks.log_config import logging_info,logging_error
import time
from stocks.models import StockInfo
import pdb
class WebScraperFetcher:
    def fetch_data(self, symbol, max_retries,retry_delay):
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
        """使用爬蟲抓取股票資料"""
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        attempt = 0  # 初始化重試次數
        while attempt < max_retries:
            try:
                logging_info(f"爬蟲開始 : https://finance.yahoo.com/quote/{symbol}/")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                response_text = response.text
                soup = BeautifulSoup(response_text, 'html.parser')
                current_price_span = soup.find('span', {'data-testid': 'qsp-price'})
                if current_price_span:
                    current_price = current_price_span.text.strip()
                other_price_span = soup.find('div', {'data-testid': 'quote-statistics'})
                if other_price_span:
                    # 提取前收盤價
                    previous_close = other_price_span.find('fin-streamer', {'data-field': 'regularMarketPreviousClose'})
                    previous_close = previous_close.text.strip() if previous_close else None
                    # 提取開盤價
                    open_price = other_price_span.find('fin-streamer', {'data-field': 'regularMarketOpen'})
                    open_price = open_price.text.strip() if open_price else None
                    # 提取最高價與最低價（Day's Range）
                    day_range = other_price_span.find('fin-streamer', {'data-field': 'regularMarketDayRange'})
                    if day_range:
                        high_price, low_price = day_range.text.strip().split(' - ')  # 最高價與最低價
                    else:
                        high_price = low_price = None
                    # 提取成交量
                    volume = other_price_span.find('fin-streamer', {'data-field': 'regularMarketVolume'})
                    volume = volume.text.strip() if volume else None
                    # 日前殖利率
                    forward_dividend_yield  = other_price_span.find('span', title="Forward Dividend & Yield")
                    forward_dividend_yield = forward_dividend_yield.find_next('span', class_='value').text.strip() if forward_dividend_yield else None
                    # 已宣告殖利率
                    Yield  = other_price_span.find('span', title="Yield")
                    Yield = Yield.find_next('span', class_='value').text.strip() if Yield else None
                else:
                    previous_close = open_price = high_price = low_price = volume = None
                # 獲取股價相關數據
                data = {
                    'Date': pd.to_datetime('today'),
                    'Current_Price': self.safe_float(current_price),
                    'Previous_Price': self.safe_float(previous_close),
                    'Open': self.safe_float(open_price),
                    'High': self.safe_float(high_price),
                    'Low': self.safe_float(low_price),
                    'Volume': self.safe_float(volume),
                    'Forward_dividend_yield': forward_dividend_yield,
                    'Yield': Yield,
                }
                logging_info(f"爬蟲結束 : {data}")
                return data


            except Exception as e:
                attempt += 1
                if attempt < max_retries:
                    logging_info(f"等待 {retry_delay} 秒後重新嘗試... 試次 {attempt}/{max_retries} 錯誤資訊為 {e}")
                    time.sleep(retry_delay)  # 重試前等待指定的延遲時間
                else:
                    logging_error(f"重試 {max_retries} 次後仍然失敗，放棄爬取 {symbol} 資料 錯誤資訊為 {e}")
                    return None  # 重試次數用盡後返回 None
    def safe_float(self,value):
        """安全地將字符串轉換為浮點數，若遇到'X0.00'或其他無效數據則返回0"""
        if value == 'X0.00':
            return 0.0  # 如果是 'X0.00'，返回
        try:
            return float(value.replace(',', ''))  # 去掉千分位逗號，並轉換為浮點數
        except ValueError:
            return 0.0  # 當轉換失敗時，返回0