from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from datetime import date, timedelta
from django.shortcuts import render, redirect
from .models import Timesheet, TimesheetEntry, PayrollSettings, Employee
from calendarapp.models import Event
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages

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

    def _week_bounds(self, monday):
        days = [monday + timedelta(days=i) for i in range(7)]
        return days, days[0], days[-1]

    def get(self, request):
        # ?week=YYYY-MM-DD (понедельник)
        today = timezone.localdate()
        monday = request.GET.get('week')
        if monday:
            y,m,d = map(int, monday.split('-'))
            monday = date(y,m,d)
        else:
            monday = today - timedelta(days=today.weekday())
        days, week_start, week_end = self._week_bounds(monday)

        rows = [{'employee': e, 'cells': [{'hours': 0} for _ in days], 'total': 0}
                for e in Employee.objects.order_by('full_name')]
        return render(request, self.template_name, {
            'week_start': week_start, 'week_end': week_end, 'days': days, 'rows': rows
        })


class PayrollCalcView(LoginRequiredMixin, View):
    template_name = 'employees/payroll_calc.html'

    def get(self, request):
        settings = PayrollSettings.objects.first() or PayrollSettings.objects.create()
        revenue = Event.objects.filter(status='paid').aggregate(s=Sum('prepayment_amount'))['s'] or 0
        kitchen = revenue * (settings.kitchen_percent/100)
        service = revenue * (settings.service_percent/100)
        return render(request, self.template_name, {
            'revenue': revenue, 'kitchen': kitchen, 'service': service, 'settings': settings
        })
