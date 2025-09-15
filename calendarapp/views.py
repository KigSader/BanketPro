from django.views import generic
from .models import Event
from datetime import date, timedelta
import calendar as pycal
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import FormView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import EventCreateForm
from crm.models import Client
from django.shortcuts import redirect


class EventCreateView(LoginRequiredMixin, FormView):
    template_name = 'calendar/event_form.html'
    form_class = EventCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаём request, чтобы форма смогла проставить initial из GET (?date=&hall=&slot=)
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            event = form.save(user=self.request.user, commit=True)
        # Сразу уводим на карточку созданного мероприятия
        return redirect('calendarapp:event_detail', pk=event.pk)


@login_required
def client_suggest(request):
    """
    Подсказки по ФИО: до 3 вариантов по вхождению, нечувствительно к регистру.
    ?q=иванов
    """
    q = (request.GET.get('q') or '').strip()
    if not q:
        return JsonResponse({'results': []})

    qs = (Client.objects
          .filter(full_name__icontains=q)
          .order_by('full_name')[:3])
    data = [
        {
            'id': c.id,
            'label': c.full_name,
            'phone': c.phone or '',
            'source': c.source or '',
            'description': c.description or '',
        } for c in qs
    ]
    return JsonResponse({'results': data})


class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    template_name = 'calendar/event_detail.html'


class CalendarView(LoginRequiredMixin, generic.TemplateView):
    """
    Месячный календарь (дашборд) с 2 слотами: am/pm и вариантом 'full'.
    Рендерим существующий шаблон дашборда.
    """
    template_name = 'crm/dashboard.html'  # если твой шаблон лежит в другом месте — поправь путь

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        today = timezone.localdate()
        year = int(self.request.GET.get('year') or today.year)
        month = int(self.request.GET.get('month') or today.month)

        first = date(year, month, 1)
        # начало сетки — понедельник той недели, где 1-е число
        start = first - timedelta(days=first.weekday())

        # конец месяца
        _, days_in_month = pycal.monthrange(year, month)
        last = date(year, month, days_in_month)
        # конец сетки — воскресенье последней недели
        end = last + timedelta(days=(6 - last.weekday()))

        # Подтянем все события диапазона за раз
        events_qs = (
            Event.objects
            .filter(date__gte=start, date__lte=end)
            .select_related('client', 'hall')
            .only('id', 'date', 'slot', 'status', 'client__full_name', 'hall__name')
        )
        # Группируем события по дате
        events_by_date = {}
        for ev in events_qs:
            events_by_date.setdefault(ev.date, []).append(ev)

        # Собираем ячейки неделями (Mon..Sun)
        weeks = []
        cur = start
        while cur <= end:
            week = []
            for _ in range(7):
                day_events = events_by_date.get(cur, [])
                # найдем занятость слотов
                am = next((e for e in day_events if e.slot == 'am'), None)
                pm = next((e for e in day_events if e.slot == 'pm'), None)

                cell = {
                    'date': cur,
                    'date_str': cur.isoformat(),
                    'day': cur.day,
                    'in_month': (cur.month == month),
                    'events': day_events,  # если нужно обвести кружками из шаблона
                    'am_event': am,
                    'pm_event': pm,
                    'is_free': (am is None and pm is None),
                    'is_half': (am is None) ^ (pm is None),
                    'is_full': (am is not None and pm is not None),
                }
                week.append(cell)
                cur += timedelta(days=1)
            weeks.append(week)

        # навигация по месяцам
        prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
        next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)

        ctx.update({
            'year': year, 'month': month,
            'weeks': weeks,
            'prev_year': prev_y, 'prev_month': prev_m,
            'next_year': next_y, 'next_month': next_m,
            'today': today,
        })
        return ctx
