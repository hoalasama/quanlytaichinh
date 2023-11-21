from django.shortcuts import render, redirect
import pip._vendor.requests as requests
from .models import StockPurchase
from django.contrib import messages
from .forms import EditStockForm
from datetime import datetime 
import pandas as pd
import time
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

    stock_purchases = StockPurchase.objects.filter(owner=request.user)
    comparison_results = []

    for purchase in stock_purchases:
        symbol = purchase.symbol
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
        response = requests.get(url)
        real_time_data = response.json()

        comparison_result = {
            'id': purchase.id,
            'symbol': symbol,
            'quantity': purchase.quantity,
            'purchase_price': purchase.purchase_price,
            'real_time_price': real_time_data.get('c', 0),
        }
        comparison_results.append(comparison_result)

    return render(request, 'stocks/result.html', {'results': comparison_results})

def get_stock_price(symbol, date):
    period = int(time.mktime(date.timetuple()))
    interval = '1d'
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={period}&period2={period}&interval={interval}&events=history&includeAdjustedClose=true'
    
    try:
        df = pd.read_csv(query_string)
        return df['Close'].iloc[0]
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def simulate_purchase(request):
    default_date = datetime.today() 
    context = {
        'default_date': default_date.strftime('%Y-%m-%d'),
    }
    if request.method == 'GET':
        return render(request, 'stocks/buying.html',context)
    if request.method == 'POST':
        symbol = request.POST['symbol'].upper()
        quantity = int(request.POST['quantity'])
        date_str = request.POST['purchase_date']
        date = datetime.strptime(date_str, '%Y-%m-%d')

        purchase_price = get_stock_price(symbol, date)

        if purchase_price is None:
            error_message = f"Error: Unable to get price for {symbol} on {date_str}. Please check the symbol and date."
            context['error_message'] = error_message
            messages.error(request, 'Symbol not found')
            return render(request, 'stocks/buying.html', context)

        StockPurchase.objects.create(
            owner=request.user,
            symbol=symbol,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=date,
        )
        return redirect('stock_result')

def edit_stock(request, id):
    stock = StockPurchase.objects.get(pk=id)

    if request.method == 'POST':
        form = EditStockForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            stock.quantity = form.cleaned_data['quantity']
            stock.purchase_date = form.cleaned_data['purchase_date']
            stock.purchase_price = get_stock_price(symbol, form.cleaned_data['purchase_date'])
            stock.save()
            messages.success(request, 'Stock updated')
            return redirect('stock_result')
    else:
        form = EditStockForm(initial={
            'quantity': stock.quantity,
            'purchase_date': stock.purchase_date,
            'symbol': stock.symbol,
            'original_purchase_date': stock.purchase_date, 
        })

    return render(request, 'stocks/edit_stock.html', {'stock': stock, 'form': form})

def delete_stock(request, id):
    stock = StockPurchase.objects.get(pk=id)
    stock.delete()
    messages.success(request,'Stock removed')
    return redirect('stock_result')