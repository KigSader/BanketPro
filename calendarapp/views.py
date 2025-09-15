from django import forms
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from crm.models import Client
from .models import Event
from datetime import date, timedelta
import calendar as pycal
from django.utils import timezone

class EventForm(forms.ModelForm):
    # Полный день (второй слот создадим в form_valid)
    slot_full = forms.BooleanField(label='Полный день', required=False)

    # Создание НОВОГО клиента прямо из формы
    new_client = forms.BooleanField(label='Создать нового клиента', required=False)
    new_full_name = forms.CharField(label='ФИО', required=False)
    new_phone = forms.CharField(label='Телефон', required=False)
    new_source = forms.CharField(label='Источник', required=False)
    new_description = forms.CharField(label='Описание', required=False,
                                      widget=forms.Textarea(attrs={'rows':2,'placeholder':'Краткая заметка'}))

    class Meta:
        model = Event
        fields = ['client','hall','date','slot','title','status','guests',
                  'client_menu','extras','contract','prepayment_amount','responsible']
        labels = {
            'client': 'Клиент',
            'hall': 'Зал',
            'date': 'Дата',
            'slot': 'Время',
            'title': 'Название/повод',
            'status': 'Статус',
            'guests': 'Количество гостей',
            'client_menu': 'Меню',
            'extras': 'Доп. услуги',
            'contract': 'Договор',
            'prepayment_amount': 'Предоплата, ₽',
            'responsible': 'Ответственный',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type':'date'}),
            'slot': forms.Select(attrs={'class':'form-select'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'client': forms.Select(attrs={'class':'form-select'}),
            'hall': forms.Select(attrs={'class':'form-select'}),
            'client_menu': forms.Select(attrs={'class':'form-select'}),
            'extras': forms.SelectMultiple(attrs={'size':6, 'class':'form-select'}),
            'title': forms.TextInput(attrs={'placeholder':'Напр., Юбилей, Свадьба'}),
            'prepayment_amount': forms.NumberInput(attrs={'step':'0.01','min':'0'}),
            'guests': forms.NumberInput(attrs={'min':'0'}),
        }

    def __init__(self, *args, **kwargs):
        req = kwargs.pop('request', None)  # <- забираем request (чтобы не был unexpected kwarg)
        super().__init__(*args, **kwargs)
        if req:
            d = req.GET.get('date')
            s = req.GET.get('slot')
            cid = req.GET.get('client')
            if d:
                self.fields['date'].initial = d
            if s in ('am', 'pm'):
                self.fields['slot'].initial = s
            if s == 'full':
                # галочка "Полный день" — дублируем второй слот в form_valid
                self.fields['slot_full'].initial = True
            if cid:
                self.fields['client'].initial = cid

    def clean(self):
        data = super().clean()
        # Валидация "нового клиента"
        if data.get('new_client'):
            fn = (data.get('new_full_name') or '').strip()
            ph = (data.get('new_phone') or '').strip()
            if not fn:
                self.add_error('new_full_name', 'Укажите ФИО')
            if not ph:
                self.add_error('new_phone', 'Укажите телефон')
        else:
            if not data.get('client'):
                self.add_error('client', 'Выберите клиента или создайте нового')
        return data

class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = 'calendar/event_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # ВАЖНО: передаём request → форма его "pop" в __init__
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        # Забираем флаг "полный день" ДО сохранения (иначе KeyError/TypeError)
        full = form.cleaned_data.pop('slot_full', False)

        # Создадим клиента при необходимости
        if form.cleaned_data.get('new_client'):
            client = Client.objects.create(
                full_name=form.cleaned_data['new_full_name'],
                phone=form.cleaned_data['new_phone'],
                source=form.cleaned_data.get('new_source', ''),
                description=form.cleaned_data.get('new_description', '')
            )
            form.instance.client = client

        # Сохраняем первое событие
        response = super().form_valid(form)

        # Дублируем второй слот, если "Полный день"
        if full:
            other = 'pm' if self.object.slot == 'am' else 'am'
            Event.objects.create(
                client=self.object.client, hall=self.object.hall,
                date=self.object.date, slot=other,
                title=self.object.title, status=self.object.status,
                guests=self.object.guests, client_menu=self.object.client_menu,
                prepayment_amount=self.object.prepayment_amount,
                responsible=self.object.responsible,
            )
        return response

    def get_success_url(self):
        return reverse('calendarapp:event_detail', args=[self.object.pk])

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
            .only('id','date','slot','status','client__full_name','hall__name')
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
