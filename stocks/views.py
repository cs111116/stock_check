from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Stock
from .utils import check_stock_prices,get_drop_threshold,get_stock_name
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

def stock_list(request):
    """顯示監測中的股票列表"""
    stocks = Stock.objects.all()
    form = StockForm()  # 確保表單存在
    return render(request, "stocks/stock_list.html", {"stocks": stocks, "form": form})

def add_stock(request):
    """新增監測股票並自動計算小跌和大跌閾值"""
    form = StockForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            stock = form.save(commit=False)  # 不馬上保存，先處理其他邏輯
            stock_symbol = stock.symbol
            stock.name = get_stock_name(stock_symbol)
            try:
                stock.small_drop_threshold, stock.large_drop_threshold = get_drop_threshold(stock_symbol)
                stock.save()  # 保存股票資料

                # 成功後返回包含股票列表的 HTML
                stocks = Stock.objects.all()
                html = render(request, "stocks/stock_list.html", {"stocks": stocks}).content.decode("utf-8")
                return JsonResponse({"success": True, "html": html})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
        else:
            return JsonResponse({"success": False, "html": render(request, "stocks/add_stock_form.html", {"form": form}).content.decode("utf-8")})

    return render(request, "stocks/stock_list.html", {"form": form})


def add_stocks(request):
    """批量新增監測股票並自動計算小跌和大跌閾值"""
    if request.method == "POST":
        stock_symbols = request.POST.get("symbols")  # 從表單中獲取多個股票代號
        stock_list = stock_symbols.splitlines()  # 以換行符號分隔每個股票代號
        errors = []
        for symbol in stock_list:
            symbol = symbol.strip()  # 移除多餘的空格
            if symbol:
                # 查詢股票名稱
                try:
                    stock_name = get_stock_name(symbol)
                    stock = Stock(symbol=symbol, name=stock_name)
                    stock.small_drop_threshold, stock.large_drop_threshold = get_drop_threshold(symbol)  # 計算小跌和大跌閾值
                    stock.save()
                except Exception as e:
                    errors.append(f"無法新增 {symbol}: {str(e)}")

        if errors:
            return JsonResponse({"success": False, "errors": errors})
        # 成功後返回包含股票列表的 HTML
        stocks = Stock.objects.all()
        html = render(request, "stocks/stock_list.html", {"stocks": stocks}).content.decode("utf-8")
        return JsonResponse({"success": True, "html": html})

def delete_stock(request, stock_id):
    """刪除監測股票"""
    stock = Stock.objects.get(id=stock_id)
    stock.delete()
    return redirect("stock_list")
