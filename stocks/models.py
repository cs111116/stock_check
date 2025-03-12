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
class StockData(models.Model):
    symbol = models.CharField(max_length=10)  # 股票代號
    date = models.DateField()  # 交易日期
    open = models.DecimalField(max_digits=10, decimal_places=2)  # 開盤價
    high = models.DecimalField(max_digits=10, decimal_places=2)  # 最高價
    low = models.DecimalField(max_digits=10, decimal_places=2)  # 最低價
    close = models.DecimalField(max_digits=10, decimal_places=2)  # 收盤價
    volume = models.BigIntegerField()  # 成交量
    price_change = models.DecimalField(max_digits=10, decimal_places=2)  # 漲跌價差
    stock_splits = models.DecimalField(max_digits=10, decimal_places=2, default=1)  # 股票拆分比例
    class Meta:
        unique_together = ('symbol', 'date')
    def __str__(self):
        return f"{self.symbol} - {self.date}"
class StockInfo(models.Model):
    stock_code = models.CharField(max_length=10, unique=True)  # 股票代號
    stock_name = models.CharField(max_length=100)  # 股票名稱
    market_type = models.IntegerField(choices=[(1, 'Listed'), (2, 'OTC')])  # 市場別 (1=上市, 2=上櫃)
    security_type = models.IntegerField(choices=[(1, 'Stock'), (2, 'ETF')])  # 有價證券別 (1=股票, 2=ETF)
    industry = models.CharField(max_length=50)  # 產業別

    def __str__(self):
        return f"{self.stock_code} - {self.stock_name}"