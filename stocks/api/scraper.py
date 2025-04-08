# api/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from stocks.log_config import logging_info,logging_error
import time
from stocks.models import StockInfo
import re
import pdb

class WebScraperFetcher:
    def fetch_data(self, symbol, max_retries, retry_delay):
        if not symbol.isdigit():  # 判斷是否為數字，為台股 
            logging_error(f"無效的股票代號：{symbol}")
            return None

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
        url = f"https://tw.stock.yahoo.com/quote/{symbol}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        attempt = 0  # 初始化重試次數
        while attempt < max_retries:
            try:
                logging_info(f"爬蟲開始 : {url}")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                response_text = response.text
                
                # 使用 BeautifulSoup 解析 HTML
                soup = BeautifulSoup(response_text, 'html.parser')
                
                # 根據提供的 HTML 結構提取數據
                price_detail_items = soup.find_all('li', class_='price-detail-item')
                
                # 初始化變量
                current_price = None
                previous_close = None
                open_price = None
                high_price = None
                low_price = None
                volume = None
                Yield = None
                
                # 遍歷所有價格詳情項
                for item in price_detail_items:
                    label = item.find('span', class_='C(#232a31)')
                    value = item.find('span', class_='Fw(600)')
                    
                    if label and value:
                        label_text = label.text.strip()
                        value_text = value.text.strip()
                        
                        # 移除可能的箭頭圖標
                        arrow = value.find('span', class_='Mend(4px) Bds(s)')
                        if arrow:
                            value_text = value_text.replace(arrow.text, '').strip()
                        
                        if label_text == '成交':  # 修改這裡，確保完全匹配"成交"
                            current_price = value_text
                        elif '昨收' in label_text:
                            previous_close = value_text
                        elif '開盤' in label_text:
                            open_price = value_text
                        elif '最高' in label_text:
                            high_price = value_text
                        elif '最低' in label_text:
                            low_price = value_text
                        elif '總量' in label_text:
                            volume = value_text
                
                # 獲取股價相關數據
                data = {
                    'Date': pd.to_datetime('today'),
                    'Current_Price': self.safe_float(current_price),
                    'Previous_Price': self.safe_float(previous_close),
                    'Open': self.safe_float(open_price),
                    'High': self.safe_float(high_price),
                    'Low': self.safe_float(low_price),
                    'Volume': self.safe_float(volume),
                    'Forward_dividend_yield': None,
                    'Yield': self.safe_float(Yield),
                }
                # 如果所有數據都是 0，可能是爬取失敗
                if all(v == 0.0 for k, v in data.items() if k != 'Date' and k != 'Forward_dividend_yield' and k != 'Yield'):
                    logging_error(f"爬取失敗，無法獲取 {symbol} 的數據")
                    raise ValueError(f"爬取失敗，無法獲取 {symbol} 的數據")  # 拋出異常，讓程序進入重試機制
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

    def safe_float(self, value):
        """安全地將字符串轉換為浮點數，若遇到'X0.00'或其他無效數據則返回0"""
        if value is None:
            return 0.0  # 如果是 None，返回 0
        if value == 'X0.00':
            return 0.0  # 如果是 'X0.00'，返回 0
        try:
            # 處理可能的百分比符號和千分位逗號
            value = value.replace(',', '').replace('%', '')
            return float(value)  # 轉換為浮點數
        except ValueError:
            return 0.0  # 當轉換失敗時，返回0