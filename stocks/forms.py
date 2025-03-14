from django import forms
from .models import Stock,User
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
            'username': {
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