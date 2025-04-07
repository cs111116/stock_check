from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("stock", views.stock_list, name="stock_list"),
    path("check/", views.check_stocks, name="check_stocks"),
    path("add/",  views.add_stock, name="add_stock"),
    path("add_bulk/",  views.add_stocks, name="add_stocks"),  # 批量新增
    path("set_stock_info/",  views.set_stock_info, name="set_stock_info"),  # 批量新增
    path("delete/<int:stock_id>/",  views.delete_stock, name="delete_stock"),
    path('user/list/', views.user_list, name='user_list'),  # 顯示所有用戶
    path('user/add/', views.add_user, name='add_user'),  # 新增用戶
    path('user/get/<int:user_id>/', views.get_user, name='get_user'),
    path('user/edit/<int:user_id>/', views.edit_user, name='edit_user'),  # 編輯用戶
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),  # 刪除用戶
]
