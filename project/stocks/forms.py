from django import forms

class EditStockForm(forms.Form):
    quantity = forms.IntegerField()
    purchase_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    symbol = forms.CharField(widget=forms.HiddenInput())