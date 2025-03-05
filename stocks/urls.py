from django.urls import path
from .views import stock_list, check_stocks, delete_stock,add_stock,add_stocks

urlpatterns = [
    path("", stock_list, name="stock_list"),
    path("check/", check_stocks, name="check_stocks"),
    path("add/", add_stock, name="add_stock"),
    path("add_bulk/", add_stocks, name="add_stocks"),  # 批量新增
    path("delete/<int:stock_id>/", delete_stock, name="delete_stock"),
]
