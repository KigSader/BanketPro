from django.urls import path
from . import views

app_name = 'expenses'
urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='expense_list'),
    path('new/', views.ExpenseCreateView.as_view(), name='expense_create'),
]
