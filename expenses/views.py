import csv
from io import StringIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm

class ExpenseListView(LoginRequiredMixin, generic.ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Expense.objects.all()
        d1 = self.request.GET.get('date_from'); d2 = self.request.GET.get('date_to')
        t  = self.request.GET.get('type')
        if d1: qs = qs.filter(date__gte=d1)
        if d2: qs = qs.filter(date__lte=d2)
        if t:  qs = qs.filter(type=t)
        return qs

    def render_to_response(self, context, **kwargs):
        if self.request.GET.get('export') == 'csv':
            buf = StringIO(); w = csv.writer(buf, delimiter=';')
            w.writerow(['Дата','Тип','Сумма','Комментарий'])
            for e in context['object_list']:
                w.writerow([e.date, e.get_type_display(), e.amount, e.note])
            resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename=expenses.csv'
            return resp
        return super().render_to_response(context, **kwargs)

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        agg = ctx['object_list'].aggregate(total=Sum('amount'))
        ctx['total'] = agg['total'] or 0
        return ctx

class ExpenseCreateView(LoginRequiredMixin, generic.CreateView):
    model = Expense; form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = '/expenses/'
