import requests
from .models import Stock,StockInfo
from datetime import datetime
from stocks.log_config import logging_info,logging_error
import pdb
import os
from .api.fetch_stock_data import fetch_stock_data,fetch_history
from .api.fetch_stock_info import fetch_stock_info
from django.utils import timezone  # 添加這行在文件開頭
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# CHAT_ID = os.getenv("TEST_CHAT_ID")
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
    return data
def send_telegram_alert(stock, trend, price_change_percentage, data):
    message_lines = [
        f"{trend} {price_change_percentage:.2f}%",
        f"股票名稱/代號: {stock.name} ({stock.symbol})",
        f"當前價格: {data['Current_Price']:.2f}",
        f"今日開盤: {data['Open']:.2f}",
        f"今日最高: {data['High']:.2f}",
        f"今日最低: {data['Low']:.2f}",
        f"小跌/大跌: {stock.small_drop_threshold}% / {stock.large_drop_threshold}%",
        f"目前成交量: {(data['Volume']):.2f}張"
    ]
    if data['Forward_dividend_yield']:
        message_lines.append(f"目前殖利率(測試中): {data['Forward_dividend_yield']}")
    elif data['Yield']:
        message_lines.append(f"宣告殖利率(測試中): {data['Yield']}")
    send_message = "\n".join(message_lines)
    """發送 Telegram 通知"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {"chat_id": CHAT_ID, "text": send_message}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        logging_error("❌ 發送失敗，請檢查 BOT_TOKEN、CHAT_ID 是否正確！")

def calculate_price_change(current_price, previous_close):
    price_change = current_price - previous_close
    price_change_percentage = (price_change / previous_close) * 100
    return price_change, price_change_percentage
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
            price_change, price_change_percentage = calculate_price_change(result['Current_Price'],result['Previous_Price'])
            # 計算小跌、大跌
            if price_change < 0 and abs(price_change_percentage) >= stock.large_drop_threshold:
                if not stock.alert_sent_today:
                    trend = "🟢🟢 大跌"
                    send_telegram_alert(stock, trend, abs(price_change_percentage), result)
                    stock.alert_sent_today = True  # 標記為已發送
                    stock.last_alert_sent = timezone.now()  # 使用 timezone.now() 替代 datetime.now()
                    stock.save()
                    logging_info(f"Stock {stock.symbol} - {stock.name}: 大跌, 大跌警報已寄送")
                else:
                    logging_info(f"Stock {stock.symbol} - {stock.name}: 大跌, 今日已發送過警報")
            elif price_change < 0 and abs(price_change_percentage) >= stock.small_drop_threshold and abs(price_change_percentage) < stock.large_drop_threshold:
                if not stock.alert_sent_today:
                    trend = "🟢 小跌"
                    send_telegram_alert(stock, trend, abs(price_change_percentage), result)
                    stock.alert_sent_today = True  # 標記為已發送
                    stock.last_alert_sent = timezone.now()  # 使用 timezone.now() 替代 datetime.now()
                    stock.save()
                    logging_info(f"Stock {stock.symbol} - {stock.name}: 小跌, 小跌警報已寄送")
                else:
                    logging_info(f"Stock {stock.symbol} - {stock.name}: 小跌, 今日已發送過警報")
            else:
                logging_info(f"Stock {stock.symbol} - {stock.name}: 無顯著變動。")
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

def send_final_alert(stock, result):
    """發送結算通知"""
    message = (
        f"📊 {stock.name} ({stock.symbol}) 今日結算\n"
        f"收盤價: {result['Current_Price']}\n"
        f"開盤價: {result['Open']}\n"
        f"最高: {result['High']}\n"
        f"最低: {result['Low']}\n"
        f"成交量: {result['Volume']}\n"
    )
    # 計算漲跌幅
    price_change, price_change_percentage = calculate_price_change(result['Current_Price'], result['Previous_Price'])
    # 添加漲跌幅信息
    if price_change > 0:
        message += f"📈 上漲: {abs(price_change_percentage):.2f}%\n"
    elif price_change < 0:
        message += f"📉 下跌: {abs(price_change_percentage):.2f}%\n"
    else:
        message += "➖ 持平\n"
    # 發送 Telegram 消息
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        logging_error("❌ 發送失敗，請檢查 BOT_TOKEN、CHAT_ID 是否正確！")
    else:
        logging_info(f"已發送 {stock.name} 的收盤結算通知")

def check_final_stocks():
    """檢查用戶新增的股票並發送結算通知"""
    from stocks.models import Stock  # 改用 Stock 模型而不是 StockInfo
    stocks = Stock.objects.all()  # 獲取用戶新增的股票
    for stock in stocks:
        try:
            result = get_stock_price(stock.symbol)
            if result is None:
                logging_error(f"無法獲取 {stock.name} 的收盤資料")
                continue
            send_final_alert(stock, result)
            # 重置當日警報發送標記，為下一個交易日做準備
            stock.alert_sent_today = False
            stock.save()
        except Exception as e:
            logging_error(f"處理 {stock.name} 的結算通知時發生錯誤: {str(e)}")
            continue
