# api/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
class WebScraperFetcher:
    def fetch_data(self, symbol):
        """使用爬蟲抓取股票資料"""
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        html_file = f"{symbol}_stock_page.html"

        # 檢查本地是否已有儲存的 HTML 檔案
        if os.path.exists(html_file):
            print("Loading data from local file...")
            with open(html_file, 'r', encoding='utf-8') as file:
                response_text = file.read()
        else:
            try:
                # 從網頁抓取
                response = requests.get(url, headers=headers)
                response_text = response.text
                # 儲存到本地
                with open(html_file, 'w', encoding='utf-8') as file:
                    file.write(response_text)
                print("Saved response to local file.")
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                return None
        try:
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
            else:
                previous_close = open_price = high_price = low_price = volume = None
            # 獲取股價相關數據
            data = {
                'Date': [pd.to_datetime('today')],
                'Current Price': [current_price],
                'Previous Close': [previous_close],
                'Open Price': [open_price],
                'High Price': [high_price],
                'Low Price': [low_price],
                'Volume': [volume],
            }
            df = pd.DataFrame(data)
            return df


        except Exception as e:
            print(f"Error scraping data for {symbol}: {e}")
            return None
