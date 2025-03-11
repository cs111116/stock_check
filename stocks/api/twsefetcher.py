import requests
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from stocks.models import StockData
import pdb
from django.db import transaction
from stocks.log_config import logging_info,logging_error
import pandas as pd
class TwseFetcher:
    def fetch_history_data(self, symbol, start_date=None):
        """從台灣證券交易所抓取歷史股價資料並存入資料庫"""
        if not start_date:
            date_array = self._get_date_str_for_month()  # 默認過去六個月
        else:
            date_array = self._get_date_str_for_month(start_date)  # 根據提供的 start_date 生成資料
        # 日期為陣列，過去6個月的日期
        for date in date_array:
            # 檢查資料庫中是否已存在該股票資料
            if self.check_data_in_db(symbol, self.get_previous_valid_date(date)):
                continue  # 如果資料已存在，跳過爬取
            else:
                # 如果資料不存在，開始爬蟲
                logging_info(f"搜尋{symbol}股票 時間在{date}...")
                url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={symbol}"
                response = requests.get(url)
                # 如果回應成功，返回 JSON 資料
                if response.status_code == 200:
                    logging_info(f"Data saved for {symbol} on {date}.")
                    self.save_to_db(symbol, response.json())  # 存入資料庫
                else:
                    logging_error(f"Failed to fetch data for {symbol} on {date}. Status code: {response.status_code}")
        return self.get_data_by_date(symbol,date_array[-1],date_array[0])
    def get_data_by_date(self, symbol, start_date, end_date):
        """從資料庫取出該股票指定時間範圍內的歷史資料，並按照日期排序"""
        # 根據日期範圍篩選資料，若沒有範圍則返回所有資料
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if isinstance(end_date, str) else end_date
            data = StockData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')
        else:
            return None
        history_data = []
        for stock_data in data:
            history_data.append({
                'Date': stock_data.date.strftime('%Y-%m-%d'),
                'Close': stock_data.close,  # 收盤價
                'Open': stock_data.open,  # 開盤價
                'High': stock_data.high,  # 最高價
                'Low': stock_data.low,  # 最低價
                'Volume': stock_data.volume  # 成交量
            })
        df = pd.DataFrame(history_data)
        return df
    def _get_date_str_for_month(self, start_date=None):
        """根據當前日期，獲取過去六個月的日期（格式 YYYYMMDD）"""
        if start_date:
            # 如果提供了start_date，則轉換為datetime對象並計算月份範圍
            start_date = datetime.strptime(str(start_date), "%Y-%m-%d")  # 以YYYYMMDD格式解析
            current_date = datetime.today()
            months_diff = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            date_range = [start_date + relativedelta(months=i) for i in range(months_diff + 1)]
        else:
            today = datetime.today().date()
            first_day_of_previous_month = (today.replace(day=1) - relativedelta(months=1)).replace(day=1)
            date_range = [first_day_of_previous_month - relativedelta(months=i) for i in range(6)]
        date_array = [d.replace(day=1).strftime('%Y-%m-01') for d in date_range]
        return date_array

    def save_to_db(self, symbol, data):
        """將抓取的資料保存至資料庫"""
        with transaction.atomic():  # 開始事務
            for stock_data in data.get('data', []):
                try:
                    # 解析日期，將民國年轉換為西元年
                    split_date = stock_data[0].split('/')
                    gregorian_year = int(split_date[0]) + 1911
                    month = int(split_date[1])
                    date = int(split_date[2])
                    formatted_date = f"{gregorian_year}-{month:02d}-{date:02d}"  # 組合為西元年月日格式
                    if not self.check_data_in_db(symbol, formatted_date):

                        # 去除數字中的逗號並轉換為浮點數
                        open_price = self.safe_float(stock_data[3])
                        high_price = self.safe_float(stock_data[4])
                        low_price = self.safe_float(stock_data[5])
                        close_price = self.safe_float(stock_data[6])
                        volume = int(stock_data[8].replace(',', ''))  # 去除千分位逗號
                        price_change = self.safe_float(stock_data[7])  # 漲跌價差

                        # 格式化資料並儲存
                        stock_data_obj = StockData(
                            symbol=symbol,
                            date=formatted_date,  # 解析日期
                            open=open_price,  # 使用 open 代替 open_price
                            high=high_price,  # 使用 high 代替 high_price
                            low=low_price,  # 使用 low 代替 low_price
                            close=close_price,  # 使用 close 代替 close_price
                            volume=volume,  # 使用 volume 代替 volume
                            price_change=price_change  # 使用 price_change 代替 price_change
                        )
                        stock_data_obj.save()  # 儲存到資料庫

                except Exception as e:
                    logging_error(f"儲存錯誤 {symbol} 時間 {formatted_date}: {e}")
                    logging_error(f"股票資料: {stock_data}")
                    logging_error(f"儲存資料: {stock_data_obj}")
                    # 可以在此處發送錯誤通知或記錄錯誤
                    # 若有錯誤，事務將回滾
                    transaction.set_rollback(True)
                    raise  # 拋出錯誤，讓整個事務回滾並中止後續操作
    def get_previous_valid_date(self, date):
        """根据日期找出下一个有效交易日（例如工作日）"""
        date_obj = datetime.strptime(date, "%Y-%m-%d")  # 转换为日期对象
        # 设置周末逻辑，周六和周日跳转到下周一
        if date_obj.weekday() == 5:  # 如果是星期六，跳转到下周一
            date_obj += timedelta(days=2)  # 星期一
        elif date_obj.weekday() == 6:  # 如果是星期日，跳转到下周一
            date_obj += timedelta(days=1)  # 星期一
        return date_obj.strftime("%Y-%m-%d")  # 返回有效日期，格式为 YYYY-MM-DD
    def check_data_in_db(self, symbol, date):
        """檢查資料庫中是否已經存在該股票資料"""
        return StockData.objects.filter(symbol=symbol, date=date).exists()
    def safe_float(self,value):
        """安全地將字符串轉換為浮點數，若遇到'X0.00'或其他無效數據則返回0"""
        if value == 'X0.00':
            return 0.0  # 如果是 'X0.00'，返回0
        try:
            return float(value.replace(',', ''))  # 去掉千分位逗號，並轉換為浮點數
        except ValueError:
            return 0.0  # 當轉換失敗時，返回0