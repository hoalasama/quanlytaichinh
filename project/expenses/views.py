from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from datetime import date as dt
# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)


    context = {
        'expenses': expenses
    }
    return render(request, 'expenses/index.html', context)


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