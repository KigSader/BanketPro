from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
  path('', views.EmployeeListView.as_view(), name='employee_list'),
  path('new/', views.EmployeeCreateView.as_view(), name='employee_create'),
  path('timesheet/', views.TimesheetWeekView.as_view(), name='timesheet_week'),
  path('payroll/', views.PayrollCalcView.as_view(), name='payroll_calc'),
]
