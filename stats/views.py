from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.db.models import Sum
from django.utils import timezone
from expenses.models import Expense
from employees.models import PayrollSettings
from calendarapp.models import Event

class DashboardStatsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'stats/dashboard.html'
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        d1 = self.request.GET.get('date_from'); d2 = self.request.GET.get('date_to')
        ev = Event.objects.all()
        ex = Expense.objects.all()
        if d1: ev = ev.filter(date__gte=d1); ex = ex.filter(date__gte=d1)
        if d2: ev = ev.filter(date__lte=d2); ex = ex.filter(date__lte=d2)
        revenue = ev.filter(status='paid').aggregate(s=Sum('prepayment_amount'))['s'] or 0
        expenses = ex.aggregate(s=Sum('amount'))['s'] or 0
        ps = PayrollSettings.objects.first()
        kitchen_pct = ps.kitchen_percent if ps else 4
        service_pct = ps.service_percent if ps else 6
        kitchen = revenue * (kitchen_pct/100)
        service = revenue * (service_pct/100)
        profit = revenue - (expenses + kitchen + service)
        ctx.update(dict(
            date_from=d1, date_to=d2, revenue=revenue, expenses=expenses,
            kitchen=kitchen, service=service, profit=profit,
            kitchen_pct=kitchen_pct, service_pct=service_pct,
        ))
        return ctx
