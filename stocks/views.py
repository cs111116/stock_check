from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Stock
from .utils import check_stock_prices
from .forms import StockForm


def stock_list(request):
    """顯示監測中的股票列表"""
    stocks = Stock.objects.all()
    form = StockForm()  # 確保表單存在
    return render(request, "stocks/stock_list.html", {"stocks": stocks, "form": form})



def check_stocks(request):
    """手動觸發股票監測"""
    check_stock_prices()
    return redirect("stock_list")


def add_stock(request):
    """新增監測股票（支援 AJAX）"""
    form = StockForm(request.POST or None)  # 確保初始化 form
    if request.method == "POST":
        if form.is_valid():
            form.save()
            stocks = Stock.objects.all()
            return JsonResponse(
                {
                    "success": True,
                    "html": render(
                        request, "stocks/stock_list.html", {"stocks": stocks,"form": StockForm()}
                    ).content.decode("utf-8"),
                }
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "html": render(
                        request, "stocks/add_stock_form.html", {"form": form}
                    ).content.decode("utf-8"),
                }
            )

    return render(request, "stocks/stock_list.html", {"form": form})


def delete_stock(request, stock_id):
    """刪除監測股票"""
    stock = Stock.objects.get(id=stock_id)
    stock.delete()
    return redirect("stock_list")
