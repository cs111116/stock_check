from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # 股票代號
    threshold = models.FloatField()  # 設定的跌幅 %
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間

    def __str__(self):
        return f"{self.symbol} - {self.threshold}%"
