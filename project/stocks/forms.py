from django import forms

class EditStockForm(forms.Form):
    quantity = forms.IntegerField()
    purchase_price = forms.DecimalField()