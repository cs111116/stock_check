from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from .models import Stock, User, UserStock
from .utils import check_stock_prices,get_drop_threshold,get_stock_name,set_stokc_info
from .forms import StockForm, UserForm
import pdb

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

def set_stock_info(request):
    set_stokc_info()
    return redirect("stock_list")

def render_table(users):
    """渲染用戶表格"""
    return render_to_string("stocks/user_list.html", {
        "users": users,
        "form": UserForm(),
        "render_table_only": True  # 添加這個標記
    })

def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password1"])
                user.save()
                users = User.objects.all()
                html = render_table(users)
                return JsonResponse({"success": True, "html": html})
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "errors": {
                        "general": [str(e)]
                    }
                })
        else:
            field_errors = {}
            for field, errors in form.errors.items():
                field_errors[field] = [str(error) for error in errors]
            return JsonResponse({
                "success": False,
                "errors": field_errors
            })
    else:
        form = UserForm()
    return render(request, "stocks/user_list.html", {"users": User.objects.all(), "form": form})

def get_user(request, user_id):
    """獲取用戶信息"""
    try:
        user = User.objects.get(id=user_id)
        return JsonResponse({
            "success": True,
            "user": {
                "username": user.username,
                "email": user.email
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "errors": ["用戶不存在"]
        })

def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if request.method == "POST":
            data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
            }
            if User.objects.exclude(id=user_id).filter(username=data['username']).exists():
                return JsonResponse({
                    "success": False,
                    "errors": {
                        "username": ["該用戶名已被使用"]
                    }
                })
            if User.objects.exclude(id=user_id).filter(email=data['email']).exists():
                return JsonResponse({
                    "success": False,
                    "errors": {
                        "email": ["該郵箱已被使用"]
                    }
                })
            user.username = data['username']
            user.email = data['email']
            user.save()
            users = User.objects.all()
            html = render_table(users)
            return JsonResponse({
                "success": True,
                "html": html
            })
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "errors": ["用戶不存在"]
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "errors": [str(e)]
        }, status=500)

def delete_user(request, user_id):
    if request.method == "POST":
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            users = User.objects.all()
            html = render_table(users)
            return JsonResponse({
                "success": True,
                "html": html
            })
        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "errors": ["用戶不存在"]
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "errors": [str(e)]
            }, status=500)
    return JsonResponse({
        "success": False,
        "errors": ["無效的請求方法"]
    }, status=405)

def user_list(request):
    form = UserForm(request.POST or None)
    users = User.objects.all()  # 獲取所有用戶
    return render(request, 'stocks/user_list.html', {'users': users,'form': form})