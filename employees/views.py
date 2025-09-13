from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from datetime import date, timedelta
from django.shortcuts import render, redirect
from .models import Timesheet, TimesheetEntry, PayrollSettings, Employee
from calendarapp.models import Event
from django.db.models import Sum
from django.http import HttpResponse


class EmployeeListView(LoginRequiredMixin, generic.ListView):
    model = Employee
    template_name = 'employees/employee_list.html'


class EmployeeCreateView(LoginRequiredMixin, generic.CreateView):
    model = Employee
    fields = ['full_name','phone','position','hourly_rate','category','contract','passport','med_book']
    template_name = 'employees/employee_form.html'
    success_url = '/employees/'


class TimesheetWeekView(LoginRequiredMixin, View):
    template_name = 'employees/timesheet_week.html'

    def get(self, request):
        return HttpResponse("Табель: раздел в разработке")

    def get(self, request):
        # ?week=YYYY-MM-DD (понедельник)
        week = request.GET.get('week')
        # ... вычисли диапазон Mon..Sun, выведи форму
        # (минимальная реализация: табличка с input hours[emp_id][day])
        return render(request, self.template_name)


class PayrollCalcView(LoginRequiredMixin, View):
    template_name = 'employees/payroll_calc.html'

    def get(self, request):
        return HttpResponse("Расчёт зарплаты: раздел в разработке")