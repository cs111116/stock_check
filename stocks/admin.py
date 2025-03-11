# admin.py
from django.contrib import admin
from stocks.models import StockData

admin.site.register(StockData)
