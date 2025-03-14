from django.contrib import admin
from stocks.models import StockData, Stock, StockInfo,User

admin.site.register(StockData)
admin.site.register(Stock)
admin.site.register(StockInfo)
admin.site.register(User)