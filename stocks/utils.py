import requests
import yfinance as yf
from .models import Stock

BOT_TOKEN = "7691246262:AAEEx70GbRT2wpBF4r65iNVsAiKALQZ12MQ"
CHAT_ID = "523479096"
def get_stock_price(symbol):
    """從 Yahoo Finance API 獲取股票即時價格"""
    stock = yf.Ticker(symbol)
    history = stock.history(period="1d")  # 取最近一天的數據
    return history["Close"].iloc[-1]  # 取最近的收盤價
def send_telegram_alert(message):
    print("⚡ send_telegram_alert() 函式被執行！")
    """發送 Telegram 通知"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    print("📢 發送請求到 Telegram API...")
    print(f"🔗 API URL: {url}")
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("📝 API 回應碼:", response.status_code)  # HTTP 狀態碼
    print("🔍 API 回應:", response.text)  # API 回應內容

    if response.status_code != 200:
        print("❌ 發送失敗，請檢查 BOT_TOKEN、CHAT_ID 是否正確！")

def check_stock_prices():
    """檢查股票價格並回報目前的股價與漲跌幅"""
    for stock in Stock.objects.all():
        current_price = get_stock_price(stock.symbol)  # 取得即時價格
        previous_close = get_stock_price(stock.symbol)  # 取昨日收盤價
        
        # 計算漲跌幅
        price_change = current_price - previous_close
        price_change_percentage = (price_change / previous_close) * 100

        # 決定是上漲還是下跌
        if price_change < 0:
            trend = "🔻 下跌"
        elif price_change > 0:
            trend = "🟢 上漲"
        else:
            trend = "⚖️ 無變動"

        # 組合訊息
        alert_message = (
            f"{trend} {abs(price_change_percentage):.2f}%\n"
            f"📈 股票代號: {stock.symbol}\n"
            f"💰 目前價格: {current_price:.2f} USD\n"
            f"📉 昨日收盤價: {previous_close:.2f} USD\n"
            f"📊 變動幅度: {price_change:.2f} USD"
        )

        # 發送通知
        send_telegram_alert(alert_message)
