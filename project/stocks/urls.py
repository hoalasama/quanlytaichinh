from django.urls import path
from .views import stock_info,simulate_purchase,stock_result,edit_stock,delete_stock

urlpatterns = [
    path('stocks/', stock_info, name='stock_info'),
    path('result/', stock_result, name='stock_result'),
    path('buying.html', simulate_purchase, name='simulate_purchase'),
    path('delete_stock/<int:id>', delete_stock, name='delete_stock'),
    path('edit_stock/<int:id>', edit_stock, name='edit_stock'),
]