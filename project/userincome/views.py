from django.shortcuts import render,redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib.auth.decorators import login_required
from datetime import date as dt
from django.contrib import messages
from django.http import JsonResponse
import json
import datetime
from django.db.models import Sum
from decimal import Decimal
from expenses.models import Expense
# Create your views here.


def search_income(request):
    if request.method=="POST":
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith = search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith = search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains = search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains = search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

def calculate_tax(request):
    total_income = UserIncome.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum']

    total_income = max(total_income, 0) if total_income is not None else 0

    total_income = Decimal(total_income)

    if total_income <= 5000000:
        tax = total_income * Decimal('0.05')
    elif total_income <= 10000000:
        tax = total_income * Decimal('0.1') - Decimal('250000')
    elif total_income <= 18000000:
        tax = total_income * Decimal('0.15') - Decimal('750000')
    elif total_income <= 32000000:
        tax = total_income * Decimal('0.2') - Decimal('1650000')
    elif total_income <= 52000000:
        tax = total_income * Decimal('0.25') - Decimal('3250000')
    elif total_income <= 80000000:
        tax = total_income * Decimal('0.3') - Decimal('5850000')
    else:
        tax = total_income * Decimal('0.35') - Decimal('9850000')

    tax = round(tax, 2)

    return tax  

@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    tax = calculate_tax(request)

    total_incomes = UserIncome.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum']
    total_incomes = Decimal(total_incomes)

    total_expenses = Expense.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum']
    total_expenses = Decimal(total_expenses) if total_expenses is not None else Decimal('0.00')
    
    left_over = total_incomes - total_expenses - tax
    
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        'tax': tax,
        'total_incomes': total_incomes,
        'left_over': left_over,
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    default_date = dt.today() 
    context={
            'sources': sources,
            'default_date': default_date.strftime('%Y-%m-%d'),
            'values': request.POST,
        }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method =='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)
        
        UserIncome.objects.create(owner = request.user,amount = amount, date = date,
                               source = source, description = description)
        messages.success(request, 'Income saved!!')

        return redirect('income')
    
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    
    context={
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        context['values'].date = income.date.strftime('%Y-%m-%d')
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        
        # UserIncome.objects.create(owner = request.user,amount = amount, date = date,
        #                        category = category, description = description)
        
        income.amount=amount
        income.date=date
        income.source=source
        income.description=description

        income.save()
        messages.success(request, 'Income updated!!')

        return redirect('income')


def delete_income(request, id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'Income removed')
    return redirect('income')


def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user,date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_source(income):
        return income.source 
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount=0
        filtered_by_source=incomes.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in  incomes:
        for y in source_list:
            finalrep[y]=get_income_source_amount(y)

    return JsonResponse({'income_source_data': finalrep}, safe=False)

def income_stats_view(request):
    return render(request, 'income/stats.html')