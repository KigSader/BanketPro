from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date, timedelta
from calendar import monthrange
from .models import Client
from calendarapp.models import Event
from django.http import JsonResponse
from django.urls import reverse_lazy


class ClientListView(LoginRequiredMixin, generic.ListView):
    model = Client
    paginate_by = 20
    template_name = 'crm/client_list.html'

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        q = self.request.GET.get('q')
        event_date = self.request.GET.get('event_date')
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
        if event_date:
            qs = qs.filter(events__date=event_date).distinct()
        return qs.annotate(event_count=Count('events'))


class ClientCreateView(LoginRequiredMixin, generic.CreateView):
    model = Client
    fields = ['full_name','phone','description','source']
    success_url = '/crm/clients/'
    template_name = 'crm/client_form.html'

class ClientDetailView(LoginRequiredMixin, generic.DetailView):
    model = Client
    template_name = 'crm/client_detail.html'
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx['events'] = self.object.events.select_related('hall').order_by('-date','slot')
        return ctx

class ClientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Client
    fields = ['full_name','phone','description','source']
    template_name = 'crm/client_form.html'
    success_url = reverse_lazy('crm:client_list')


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'crm/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        days_in_month = monthrange(year, month)[1]
        first_weekday = date(year, month, 1).weekday()  # 0=Mon..6=Sun

        month_start, month_end = date(year, month, 1), date(year, month, days_in_month)
        events = Event.objects.filter(date__range=(month_start, month_end)).select_related('client')

        by_day = {}
        for ev in events:
            key = ev.date.strftime('%Y-%m-%d')
            by_day.setdefault(key, {'am': None, 'pm': None})
            by_day[key][ev.slot] = ev

        days = []
        for n in range(1, days_in_month + 1):
            d_obj = date(year, month, n)
            key = d_obj.strftime('%Y-%m-%d')
            evs = by_day.get(key, {'am': None, 'pm': None})
            days.append({'n': n, 'date_str': key, 'am': evs.get('am'), 'pm': evs.get('pm')})

        leading_blanks = first_weekday
        cells = [{'blank': True}]*leading_blanks + days
        while len(cells) % 7 != 0:
            cells.append({'blank': True})
        weeks = [cells[i:i+7] for i in range(0, len(cells), 7)]

        revenue = Event.objects.filter(date__year=year, date__month=month, status='paid') \
                               .aggregate(total=Sum('prepayment_amount'))['total'] or 0

        upcoming = Event.objects.filter(
            date__gte=today, date__lte=today + timedelta(days=7)
        ).select_related('client', 'hall').order_by('date', 'slot')
        ctx['upcoming_week'] = upcoming

        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1


        ctx.update({
            'year': year, 'month': month,
            'weeks': weeks,
            'revenue': revenue,
            'today': today,
            'prev_year': prev_year, 'prev_month': prev_month,
            'next_year': next_year, 'next_month': next_month,
        })
        return ctx

def clients_search(request):
    q = (request.GET.get('q') or '').strip()
    qs = Client.objects.none()
    if q:
        qs = Client.objects.filter(Q(full_name__icontains=q) | Q(phone__icontains=q)).order_by('full_name')[:20]
    return JsonResponse([{'id':c.id,'full_name':c.full_name,'phone':c.phone} for c in qs], safe=False)
