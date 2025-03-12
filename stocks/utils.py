import requests
from .models import Stock,StockInfo
from datetime import datetime
from stocks.log_config import logging_info,logging_error
import pdb
import os
from .api.fetch_stock_data import fetch_stock_data,fetch_history
from .api.fetch_stock_info import fetch_stock_info
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# CHAT_ID = os.getenv("TEST_CHAT_ID")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
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
    history = fetch_history(symbol)
    if history is None:
        logging_error(f"撈不到{symbol}歷史資料")
        raise
    try:
        daily_pct_change1 = calculate_pct_change(history)
        small_drop_threshold = calculate_threshold(daily_pct_change1, num_std_dev=1)  # 小跌閾值（1標準差）
        large_drop_threshold = calculate_threshold(daily_pct_change1, num_std_dev=2)  # 大跌閾值（2標準差）
    except Exception as e:
        logging_error(f"計算{symbol}歷史資料錯誤: {e}")
        raise
    return abs(small_drop_threshold), abs(large_drop_threshold)

def get_stock_price(symbol):
    """從 Yahoo Finance API 獲取即時價格和前天的資料"""
    data = fetch_stock_data(symbol)
    if data is None:
       logging_error(f"資料不足，無法計算股價：{symbol}")
       return None
    # 假设 data 是一个 DataFrame，我们从中提取最后一行数据
    latest_data = data.iloc[-1]  # 获取最新的一行数据
    # 提取必要的字段
    current_price = latest_data['Current_Price']
    previous_close = latest_data['Previous_Close']
    max_price = latest_data['High_Price']
    min_price = latest_data['Low_Price']
    sell_Volume = latest_data['Volume']
    return current_price, previous_close, max_price, min_price, sell_Volume
def send_telegram_alert(message):
    """發送 Telegram 通知"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        logging_error("❌ 發送失敗，請檢查 BOT_TOKEN、CHAT_ID 是否正確！")

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
    logging_info(f"開始檢查股價")
    for stock in Stock.objects.all():
        logging_info(f"{stock.symbol}({stock.name})開始")
        try:
            result = get_stock_price(stock.symbol)
            if result is None:
                # 可以跳過處理，或者進行相應的錯誤處理
                logging_error(f"資料不足，無法處理股價：{stock.name}")
            else:
                current_price, previous_close, max_price, min_price,sell_Volume = result   # 取得即時價格
            price_change = current_price - previous_close
            price_change_percentage = (price_change / previous_close) * 100
            # 計算小跌、大跌
            if price_change < 0 and abs(price_change_percentage) >= stock.small_drop_threshold and not stock.alert_sent_today:
                trend = "🟢 小跌"
                alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                send_telegram_alert(alert_message)
                stock.alert_sent_today = True  # 標記為已發送
                # stock.save()
                logging_info(f"Stock {stock.symbol} - {stock.name}: 小跌, 小跌警報已寄送")
            elif price_change < 0 and abs(price_change_percentage) >= stock.large_drop_threshold and not stock.alert_sent_today:
                trend = "🟢🟢 大跌"
                alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                send_telegram_alert(alert_message)
                stock.alert_sent_today = True  # 標記為已發送
                # stock.save()
                logging_info(f"Stock {stock.symbol} - {stock.name}: 大跌, 大跌警報已寄送")
            else:
                logging_info(f"Stock {stock.symbol} - {stock.name}: 無顯著變動。")
                # trend = "測試"
                # alert_message = generate_alert_message(stock, trend, abs(price_change_percentage), current_price, previous_close, max_price, min_price,stock.small_drop_threshold, stock.large_drop_threshold,sell_Volume)
                # send_telegram_alert(alert_message)
            # 清除每日通知標記，讓下一次檢查重新設置
            if stock.last_alert_sent and stock.last_alert_sent.date() != datetime.today().date():
                stock.alert_sent_today = False
                stock.save()
        except Exception as e:
            logging_error(f" 發生意外的問題 {stock.symbol}: {str(e)}")
def get_stock_name(stock_symbol):
    """根據股票代號獲取股票名稱"""
    try:
        # 從資料庫中查找股票名稱
        stock_data = StockInfo.objects.filter(stock_code=stock_symbol).first()
        if stock_data:
            return stock_data.stock_name  # 如果找到對應的股票，回傳股票名稱
        else:
            logging_info(f"資料庫找不到該股票{stock_symbol}")
            return stock_symbol  # 如果找不到，回傳股票代號
    except Exception as e:
        logging_error(f"發生錯誤: {e}")
        return stock_symbol  # 如果發生錯誤，回傳股票代號
def set_stokc_info():
    try:
        data = fetch_stock_info()
        if not data:
            return None
        return data
    except Exception as e:
        return None
