from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["symbol"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["symbol"].widget.attrs.update({"class": "form-control", "placeholder": "輸入股票代號"})
