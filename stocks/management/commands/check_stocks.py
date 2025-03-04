from django.core.management.base import BaseCommand
from stocks.models import Stock
from stocks.utils import get_stock_price, send_telegram_alert

class Command(BaseCommand):
    help = "自動檢查股票價格，並發送 Telegram 通知"

    def handle(self, *args, **kwargs):
        for stock in Stock.objects.all():
            current_price = get_stock_price(stock.symbol)
            previous_close = get_stock_price(stock.symbol)  # 取昨日收盤價
            drop_percentage = ((previous_close - current_price) / previous_close) * 100

            if drop_percentage >= stock.threshold:
                alert_message = f"⚠️ {stock.symbol} 下跌 {drop_percentage:.2f}%！\n目前價格：{current_price} USD"
                send_telegram_alert(alert_message)
                self.stdout.write(self.style.WARNING(alert_message))
            else:
                self.stdout.write(self.style.SUCCESS(f"{stock.symbol} 變動 {drop_percentage:.2f}%，未達閾值"))
