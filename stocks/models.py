from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    email = models.EmailField(unique=True)  # 用戶的電子郵件
    password = models.CharField(max_length=255)  # 用戶的密碼
    chat_id = models.CharField(max_length=255, blank=True, null=True)  # 用來發送通知的 Telegram chat_id
    is_active = models.BooleanField(default=True)  # 用戶是否活躍

    # 修改 groups 和 user_permissions，添加 unique 的 related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='stocks_user_set',  # 避免與 auth.User.groups 發生衝突
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='stocks_user_permissions_set',  # 避免與 auth.User.user_permissions 發生衝突
        blank=True,
    )

    def __str__(self):
        return self.email
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

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')  # 訂閱的用戶
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE, related_name='subscriptions')  # 訂閱的股票
    subscribed_at = models.DateTimeField(auto_now_add=True)  # 訂閱時間

    def __str__(self):
        return f"{self.user.email} subscribes to {self.stock.stock_code}"

    class Meta:
        unique_together = ('user', 'stock')  # 確保同一個用戶不能重複訂閱同一隻股票