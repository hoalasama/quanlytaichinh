from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('calculate-tax/', views.calculate_tax, name='calculate_tax'),
    path('authentication/', include('authentication.urls')),
    path('add-income', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.income_edit, name='income-edit'),
    path('income-delete/<int:id>', views.delete_income, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name='search_income'),
    path('income_source_summary', views.income_source_summary, name="income_source_summary"),
    path('istats', views.income_stats_view, name="istats"),
    path('income_export_csv', views.income_export_csv, name="income-export-csv"),
    path('income_export_excel', views.income_export_excel, name="income-export-excel"),
    path('income_export_pdf', views.income_export_pdf, name="income-export-pdf"),
]
