from django.contrib import admin
from stocks.models import StockData, Stock, StockInfo

admin.site.register(StockData)
admin.site.register(Stock)
admin.site.register(StockInfo)
