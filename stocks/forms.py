from django import forms
from .models import Stock, User, UserStock

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["symbol"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["symbol"].widget.attrs.update({"class": "form-control", "placeholder": "輸入股票代號"})

class UserForm(forms.ModelForm):
    username = forms.CharField(label="暱称")
    email = forms.CharField(label="信箱")
    password1 = forms.CharField(label="密碼", widget=forms.PasswordInput)
    password2 = forms.CharField(label="確認密碼", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
            'username': {
                'required': '用戶名是必填的',
            },
            'email': {
                'required': '信箱是必填的',
            },
            'password1': {
                'required': '密碼是必填的',
            },
            'password2': {
                'required': '確認密碼是必填的',
                'invalid': '確認密碼不正確',
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("兩個密碼欄位必須相同")
        return password2

class UserStockForm(forms.ModelForm):
    symbol = forms.CharField(
        label="股票代號",
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入股票代號'
        })
    )
    class Meta:
        model = UserStock
        fields = ['target_price', 'alert_percentage']
        widgets = {
            'target_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入目標價格'
            }),
            'alert_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入提醒百分比',
                'min': '0.01',
                'step': '0.01'
            })
        }
        labels = {
            'target_price': '目標價格',
            'alert_percentage': '提醒百分比 (%)'
        }
        error_messages = {
            'symbol': {
                'required': '股票代號是必填的',
                'invalid': '請輸入有效的股票代號'
            },
            'target_price': {
                'required': '目標價格是必填的',
                'invalid': '請輸入有效的價格'
            },
            'alert_percentage': {
                'required': '提醒百分比是必填的',
                'invalid': '請輸入有效的百分比'
            }
        }

    def clean_symbol(self):
        symbol = self.cleaned_data.get('symbol')
        if symbol:
            # 檢查股票是否存在
            try:
                stock = Stock.objects.get(symbol=symbol)
                self.stock = stock
            except Stock.DoesNotExist:
                raise forms.ValidationError("找不到該股票代號")
        return symbol

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        if user:
            instance.user = user
            instance.stock = self.stock
        if commit:
            instance.save()
        return instance