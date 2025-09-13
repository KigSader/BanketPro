from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.db.models import Sum
from datetime import date
from calendarapp.models import Event
from expenses.models import Expense
from employees.models import PayrollSettings

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

        settings = PayrollSettings.objects.first()
        k_pct = (settings.kitchen_percent if settings else 0) or 0
        s_pct = (settings.service_percent if settings else 0) or 0
        kitchen = revenue * (k_pct/100)
        service = revenue * (s_pct/100)

        profit = revenue - (expenses + kitchen + service)

        ctx.update(dict(
            revenue=revenue, expenses=expenses, kitchen=kitchen, service=service, profit=profit,
            date_from=d1, date_to=d2, kitchen_pct=k_pct, service_pct=s_pct,
        ))
        return ctx
