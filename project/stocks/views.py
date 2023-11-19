from django.shortcuts import render, redirect
import pip._vendor.requests as requests
from .models import StockPurchase
from django.contrib import messages
from .forms import EditStockForm
# Create your views here.
def stock_info(request):
    api_key = 'clbolp1r01qp535t0pigclbolp1r01qp535t0pj0'
    symbol = 'AAPL'
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'

    response = requests.get(url)
    data = response.json()

    context = {'stock_data': data}

    return render(request, 'stocks/stock_info.html', context)

def stock_result(request):
    api_key = 'clbolp1r01qp535t0pigclbolp1r01qp535t0pj0'
    symbol = 'AAPL'
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
    response = requests.get(url)
    real_time_data = response.json()

    stock_purchases = StockPurchase.objects.filter(owner=request.user)

    comparison_results = []

    for purchase in stock_purchases:
        comparison_result = {
            'id': purchase.id,
            'symbol': purchase.symbol,
            'quantity': purchase.quantity,
            'purchase_price': purchase.purchase_price,
            'real_time_price': real_time_data.get('c', 0),
        }
        comparison_results.append(comparison_result)
    return render(request, 'stocks/result.html', {'results': comparison_results})


def simulate_purchase(request):
    if request.method == 'GET':
        return render(request, 'stocks/buying.html')
    if request.method == 'POST':
        symbol = request.POST['symbol'].upper()
        quantity = int(request.POST['quantity'])
        purchase_price = float(request.POST['purchase_price'])

        StockPurchase.objects.create(
            owner=request.user,
            symbol=symbol,
            quantity=quantity,
            purchase_price=purchase_price
        )
        return redirect('stock_result')

def edit_stock(request, id):
    stock = StockPurchase.objects.get(pk=id)

    if request.method == 'POST':
        form = EditStockForm(request.POST)
        if form.is_valid():
            stock.quantity = form.cleaned_data['quantity']
            stock.purchase_price = form.cleaned_data['purchase_price']
            stock.save()
            messages.success(request, 'Stock updated')
            return redirect('stock_result')
    else:
        form = EditStockForm(initial={'quantity': stock.quantity, 'purchase_price': stock.purchase_price})

    return render(request, 'stocks/edit_stock.html', {'stock': stock, 'form': form})

def delete_stock(request, id):
    stock = StockPurchase.objects.get(pk=id)
    stock.delete()
    messages.success(request,'Stock removed')
    return redirect('stock_result')