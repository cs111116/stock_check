import requests
import json
import os
from datetime import datetime, timedelta

class TwseFetcher:
    def fetch_history_data(self, symbol, start_date=None):
        """從台灣證券交易所抓取歷史股價資料"""
        # 如果沒有提供 start_date，就默認抓取6個月前的資料
        if not start_date:
            start_date = self._get_date_str_for_month()  # 默認過去六個月
        else:
            start_date = self._get_date_str_for_month(start_date)  # 根據提供的 start_date 生成資料

        # 日期為陣列，過去6個月的日期
        for date in start_date:
            # 檢查是否有存檔
            if self.check_file(symbol, date):
                print(f"File for {symbol} on {date} exists. Skipping fetch.")
                continue  # 如果檔案已存在，跳過爬取
            else:
                # 如果檔案不存在，開始爬蟲
                print(f"Fetching data for {symbol} on {date}...")
                url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={symbol}"
                response = requests.get(url)
                # 如果回應成功，返回 JSON 資料
                if response.status_code == 200:
                    self.save_file(symbol, date, response.json())  # 存檔
                    print(f"Data saved for {symbol} on {date}.")
                else:
                    print(f"Failed to fetch data for {symbol} on {date}. Status code: {response.status_code}")
        return None

    def _get_date_str_for_month(self, start_date=None):
        """根據當前日期，獲取過去六個月的日期（格式 YYYYMMDD）"""
        # 如果沒有提供 start_date，默認抓取六個月前的資料
        today = datetime.today()

        if start_date:
            # 如果提供了start_date，則轉換為datetime對象並計算六個月內的日期範圍
            start_date = datetime.strptime(str(start_date), "%Y%m")
            date_range = [start_date + timedelta(days=30 * i) for i in range(6)]  # 近6個月
        else:
            # 默認抓取六個月內的日期
            date_range = [today - timedelta(days=30 * i) for i in range(6)]

        # 格式化為YYYYMM01
        date_array = [d.replace(day=1).strftime('%Y%m01') for d in date_range]  # 抓取每個月的1號
        return date_array

    def save_file(self, symbol, date, data):
        """將抓取的資料保存至文件"""
        directory = f"{symbol}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = f"{directory}/{date}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved in {file_path}")

    def check_file(self, symbol, date):
        """檢查資料檔案是否存在"""
        file_path = f"{symbol}/{date}.json"
        return os.path.exists(file_path)
