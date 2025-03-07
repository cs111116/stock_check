import requests
from .models import Stock
from datetime import datetime
from django.conf import settings
import logging
import json
import pdb
import os
from .api.fetch_stock_data import fetch_stock_data,fetch_history
BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")
CHAT_ID = os.getenv("TEST_CHAT_ID")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
logging.basicConfig(
    filename='stock_check.log',  # 設定 log 文件名稱
    level=logging.INFO,  # 設定日誌等級
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日誌格式
    encoding='utf-8'
)

def calculate_pct_change(history):
    """計算每日收盤價的百分比變動"""
    return history['Close'].pct_change() * 100

def calculate_threshold(pct_change, num_std_dev=1):
    """計算閾值，基於過去股價的標準差"""
    mean = pct_change.mean()
    std_dev = pct_change.std()
    threshold = mean - (num_std_dev * std_dev)
    return round(threshold, 2)

def get_drop_threshold(symbol):
    """計算小跌與大跌閾值，基於過去六個月股價的標準差"""
    history = fetch_history(symbol,'20250101')
    pdb.set_trace()
    if history is None:
        return None, None
    daily_pct_change = calculate_pct_change(history)
    small_drop_threshold = calculate_threshold(daily_pct_change, num_std_dev=1)  # 小跌閾值（1標準差）
    large_drop_threshold = calculate_threshold(daily_pct_change, num_std_dev=2)  # 大跌閾值（2標準差）
    return abs(small_drop_threshold), abs(large_drop_threshold)

def get_stock_price(symbol):
    """從 Yahoo Finance API 獲取即時價格和前天的資料"""
    data = fetch_stock_data(symbol)
    if data is None:
       logging.error(f"資料不足，無法計算股價：{symbol}")
       print(f"資料不足，無法計算股價：{symbol}")
       return None
    return data
def send_telegram_alert(message):
    """發送 Telegram 通知"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        print("❌ 發送失敗，請檢查 BOT_TOKEN、CHAT_ID 是否正確！")

def generate_alert_message(stock, trend, price_change_percentage, current_price, previous_close, max_price, min_price,small_drop_threshold, large_drop_threshold,sell_Volume):
    """生成警報訊息"""
    return (
        f"{trend} {price_change_percentage:.2f}%\n"
        f"股票名稱/代號: {stock.name}({stock.symbol})\n"
        f"當前價格: {current_price:.2f}\n"
        f"昨日收盤: {previous_close:.2f}\n"
        f"今日最高: {max_price:.2f}\n"
        f"今日最低: {min_price:.2f}\n"
        f"小跌/大跌: {small_drop_threshold}% / {large_drop_threshold}%\n"
        f"目前成交量: {sell_Volume}"
    )

def check_stock_prices():
    """檢查股票價格並回報目前的股價與漲跌幅"""
    for stock in Stock.objects.all():
        try:
            result = get_stock_price(stock.symbol)
            if result is None:
                # 可以跳過處理，或者進行相應的錯誤處理
                print(f"資料不足，無法處理股價：{stock.name}")
            else:
                current_price, previous_close, max_price, min_price,sell_Volume = result   # 取得即時價格
            price_change = current_price - previous_close
            price_change_percentage = (price_change / previous_close) * 100
            # 計算小跌、大跌
            if price_change < 0 and abs(price_change_percentage) >= stock.small_drop_threshold and not stock.alert_sent_today:
                trend = "🟢 小跌"
                alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                send_telegram_alert(alert_message)
                # stock.alert_sent_today = True  # 標記為已發送
                # stock.save()
                logging.info(f"Stock {stock.symbol} - {stock.name}: 下跌, alert sent.")
            elif price_change < 0 and abs(price_change_percentage) >= stock.large_drop_threshold and not stock.alert_sent_today:
                trend = "🟢🟢 大跌"
                alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                send_telegram_alert(alert_message)
                # stock.alert_sent_today = True  # 標記為已發送
                # stock.save()
                logging.info(f"Stock {stock.symbol} - {stock.name}: 大跌, alert sent.")
            else:
                trend = "測試"
                alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                send_telegram_alert(alert_message)
            # 清除每日通知標記，讓下一次檢查重新設置
            if stock.last_alert_sent and stock.last_alert_sent.date() != datetime.today().date():
                stock.alert_sent_today = False
                stock.save()
        except Exception as e:
            logging.error(f"Error checking stock {stock.symbol}: {str(e)}")

def get_filename_for_today():
    """生成當前日期的檔案名稱"""
    return f"{datetime.now().strftime('%Y%m%d')}_stock_data.json"

def check_and_update_stock_data():
    """檢查並更新股票資料"""
    file_path = os.path.join(settings.MEDIA_ROOT, "stock_data", get_filename_for_today())

    # 檢查檔案是否存在
    if os.path.exists(file_path):
        # 檔案存在，檢查是否是今天的
        return load_stock_data(file_path)
    else:
        # 檔案不存在或已過期，重新下載資料
        return download_and_save_stock_data(file_path)

def download_and_save_stock_data(file_path):
    """從 API 下載資料並儲存"""
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # 確保資料夾存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 儲存資料到檔案
        with open(file_path, 'w') as f:
            json.dump(data, f)

        print(f"資料已下載並儲存: {file_path}")
        return data
    else:
        print("資料下載失敗，請檢查 API 設定")
        return None

def load_stock_data(file_path):
    """載入本地的股票資料"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"無法找到資料檔案: {file_path}")
        return None

def get_stock_name(stock_symbol):
    """根據股票代號獲取股票名稱"""
    try:
        # 檢查並更新資料
        stock_data = check_and_update_stock_data()
        if stock_data:
            # 在資料中查找對應的股票名稱
            for stock in stock_data:
                if stock["Code"] == stock_symbol:
                    return stock["Name"]
            return stock_symbol  # 如果找不到，回傳股票代號
        else:
            return stock_symbol  # 如果資料下載失敗，回傳代號
    except Exception as e:
        print(f"發生錯誤: {e}")
        return stock_symbol  # 如果發生錯誤，回傳股票代號
