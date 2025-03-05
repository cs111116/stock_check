from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # 股票代號
    name = models.CharField(max_length=255, null=True, blank=True)  # 股票名稱
    small_drop_threshold = models.FloatField(default=0)  # 小跌閾值 (從歷史數據計算)
    large_drop_threshold = models.FloatField(default=0)  # 大跌閾值 (從歷史數據計算)
    last_alert_sent = models.DateTimeField(null=True, blank=True)  # 最後一次通知的時間
    alert_sent_today = models.BooleanField(default=False)  # 今日是否已發送通知
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間

    def __str__(self):
        return f"{self.symbol} - {self.name} - {self.small_drop_threshold}%"
