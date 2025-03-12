import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from stocks.models import StockData
import pdb
from django.db import transaction
from stocks.log_config import logging_info, logging_error
import pandas as pd
class TwseFetcher:
    def fetch_history_data(self, symbol, start_date=None):
        """從台灣證券交易所抓取歷史股價資料並存入資料庫"""
        try:
            is_data = False
            date_array = self._get_date_str_for_month(start_date)  # 默認過去六個月
            # 日期為陣列，過去6個月的日期
            for date_str in date_array:
                # 檢查資料庫中是否已存在該股票資料
                if not self.check_data_in_db(symbol, date_str):
                    # 如果資料不存在，開始爬蟲
                    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={symbol}"
                    logging_info(f"搜尋{symbol}股票 時間在{date_str}...")
                    logging_info(f"爬蟲地址為: {url}")
                    response = requests.get(url)
                    response_json = response.json()

                    # 處理無符合條件的資料或資料為空的情況
                    if response_json['stat'] == "很抱歉，沒有符合條件的資料!" or response_json['total'] == 0:
                        logging_info(f"沒有資料或沒有此上市股票 {symbol} 資料如下{response_json}")
                        continue  # 繼續處理下一個日期
                    # 如果回應成功，返回 JSON 資料並存儲
                    if response.status_code == 200:
                        self.save_to_db(symbol, response_json)  # 存入資料庫
                        is_data = True
                        logging_info(f"已爬到股票{symbol} 時間在 {date_str}.")
                    else:
                        logging_error(f"爬蟲狀態有誤 股票{symbol} 時間 {date_str}. 網頁狀態碼為: {response.status_code}")
        except Exception as e:
            logging_error(f"爬蟲發生問題 股票{symbol}: 錯誤為{str(e)}")
        if is_data:
            return self.get_data_by_date(symbol, date_array[-1], date_array[0])
        else:
            return None

    def get_data_by_date(self, symbol, start_date, end_date):
        """從資料庫取出該股票指定時間範圍內的歷史資料，並按照日期排序"""
        try:
            # 根據日期範圍篩選資料，若沒有範圍則返回所有資料
            if start_date and end_date:
                end_date = self.get_last_day_of_month(end_date)
                data = StockData.objects.filter(
                    symbol=symbol, date__range=[start_date, end_date]
                ).order_by("date")
            else:
                return None

            # 格式化資料並將其添加至 DataFrame
            history_data = []
            for stock_data in data:
                history_data.append(
                    {
                        "Date": stock_data.date.strftime("%Y-%m-%d"),
                        "Close": float(stock_data.close),  # 收盤價
                        "Open": float(stock_data.open),  # 開盤價
                        "High": float(stock_data.high),  # 最高價
                        "Low": float(stock_data.low),  # 最低價
                        "Volume": int(stock_data.volume),  # 成交量
                    }
                )
            df = pd.DataFrame(history_data)
            return df
        except Exception as e:
            logging_error(f"Error occurred while fetching data for {symbol} between {start_date} and {end_date}: {str(e)}")
            return None

    def get_last_day_of_month(self, date_str):
        """將 YYYYMMDD 轉換為該月份的最後一天"""
        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            last_day = calendar.monthrange(year, month)[1]  # 取得該月份的最後一天
            return f"{year}{month:02d}{last_day:02d}"
        except Exception as e:
            logging_error(f"Error occurred while getting the last day of month for {date_str}: {str(e)}")
            return None

    def _get_date_str_for_month(self, start_date=None):
        """根據當前日期，獲取過去六個月的日期（格式 YYYYMMDD）"""
        try:
            if start_date:
                # 確保 start_date 是 `datetime.date`
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            else:
                start_date = datetime.today().date()
            # 計算過去 6 個月的第一天
            start_date = start_date.replace(day=1) - relativedelta(months=1)
            date_array = [
                (start_date.replace(day=1) - relativedelta(months=i)).strftime("%Y%m01")
                for i in range(6)
            ]
            return date_array
        except Exception as e:
            logging_error(f"Error occurred while getting date array for {start_date}: {str(e)}")
            return []

    def save_to_db(self, symbol, data):
        """將抓取的資料保存至資料庫"""
        try:
            with transaction.atomic():  # 開始事務
                for stock_data in data.get("data", []):
                    try:
                        # 解析日期，將民國年轉換為西元年
                        split_date = stock_data[0].split("/")
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
                            volume = int(stock_data[8].replace(",", ""))  # 去除千分位逗號
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
                                price_change=price_change,  # 使用 price_change 代替 price_change
                            )
                            stock_data_obj.save()  # 儲存到資料庫
                    except Exception as e:
                        logging_error(f"Error occurred while saving data for {symbol} on {formatted_date}: {str(e)}")
                        transaction.set_rollback(True)
                        raise  # 拋出錯誤，讓整個事務回滾並中止後續操作
        except Exception as e:
            logging_error(f"Error occurred while saving data for {symbol}: {str(e)}")

    def check_data_in_db(self, symbol, date):
        """檢查資料庫中是否已經存在該股票資料"""
        try:
            return StockData.objects.filter(symbol=symbol, date=date).exists()
        except Exception as e:
            logging_error(f"Error occurred while checking if data exists in the database for {symbol} on {date}: {str(e)}")
            return False

    def safe_float(self, value):
        """安全地將字符串轉換為浮點數，若遇到'X0.00'或其他無效數據則返回0"""
        try:
            if value == "X0.00":
                return 0.0  # 如果是 'X0.00'，返回0
            return float(value.replace(",", ""))  # 去掉千分位逗號，並轉換為浮點數
        except ValueError:
            logging_error(f"Error occurred while converting value to float: {value}")
            return 0.0  # 當轉換失敗時，返回0
