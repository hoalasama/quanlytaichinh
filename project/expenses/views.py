from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from datetime import date as dt
import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
from django.db.models import Sum
from decimal import Decimal
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
# Create your views here.


def search_expenses(request):
    if request.method=="POST":
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith = search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith = search_str, owner=request.user) | Expense.objects.filter(
            description__icontains = search_str, owner=request.user) | Expense.objects.filter(
            category__icontains = search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    total_expenses = Expense.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum']
    total_expenses = Decimal(total_expenses) if total_expenses is not None else Decimal('0.00')
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        'total_expenses': total_expenses,
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    default_date = dt.today() 
    context={
            'categories': categories,
            'default_date': default_date.strftime('%Y-%m-%d'),
            'values': request.POST,
        }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method =='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)
        
        Expense.objects.create(owner = request.user,amount = amount, date = date,
                               category = category, description = description)
        messages.success(request, 'Expense saved!!')

        return redirect('expenses')        
    

def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    
    context={
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        context['values'].date = expense.date.strftime('%Y-%m-%d')
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)
        
        Expense.objects.create(owner = request.user,amount = amount, date = date,
                               category = category, description = description)
        
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description

        expense.save()
        messages.success(request, 'Expense updated!!')

        return redirect('expenses')


def delete_expense(request, id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense removed')
    return redirect('expenses')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category 
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in  expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+ "-" + str(datetime.datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category, expense.date])
    
    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+ "-" + str(datetime.datetime.now()) + '.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expense')
    row_num = 0

    number_style = xlwt.XFStyle()
    number_style.num_format_str = '#,##0'

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    default_style = xlwt.XFStyle()

    columns = ['Amount','Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner= request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            if columns[col_num] == 'Amount':
                ws.write(row_num, col_num, row[col_num], number_style)
            elif columns[col_num] == 'Date':
                ws.write(row_num, col_num, row[col_num].strftime('%Y-%m-%d'), default_style)
            else:
                ws.write(row_num, col_num, row[col_num], default_style)

    wb.save(response)
    
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='inline; attachment; filename=Expenses'+ "-" + str(datetime.datetime.now()) + '.pdf'

    response['Cotent-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    sumExpenses = Expense.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum']
    sumExpenses = Decimal(sumExpenses) if sumExpenses is not None else Decimal('0.00')

    html_string = render_to_string('expenses/pdf-output.html', {'expenses':expenses,'total':sumExpenses})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        response.write(output.read())

    return response