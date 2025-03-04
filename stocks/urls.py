from django.urls import path
from .views import stock_list, check_stocks, delete_stock,add_stock

urlpatterns = [
    path("", stock_list, name="stock_list"),
    path("check/", check_stocks, name="check_stocks"),
    path("add/", add_stock, name="add_stock"),
    path("delete/<int:stock_id>/", delete_stock, name="delete_stock"),
]
