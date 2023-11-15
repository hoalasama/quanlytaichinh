from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='expenses'),
    path('authentication/', include('authentication.urls')),
    path('add-expense', views.add_expense, name='add-expenses'),
    path('edit-expense/<int:id>', views.expense_edit, name='expense-edit'),
    path('expense-delete/<int:id>', views.delete_expense, name='expense-delete'),
]
