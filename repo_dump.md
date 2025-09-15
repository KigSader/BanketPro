# Repository dump


---
## banketpro\settings.py
```py
from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')
DEBUG = config('DEBUG', default='True').lower() == 'true'
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'calendarapp.apps.CalendarappConfig',

    # Apps
    'crm',
    'menuapp',
    'employees',
    'warehouse',
    'expenses',
    'stats',
    'settingsapp',
    'taskapp',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # статика
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'banketpro.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'banketpro.wsgi.application'

# DB: по умолчанию SQLite (простая локальная разработка)
ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')
if ENGINE == 'django.db.backends.sqlite3':
    DATABASES = { /* redacted for dump */ }}
else:
    DATABASES = { /* redacted for dump */ },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Аутентификация
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/crm/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Сессия "как кэш" — чтобы подхватывалась между визиткой и CRM
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 дней
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

```


---
## banketpro\urls.py
```py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password_reset...

    path('crm/', include('crm.urls')),
    path('calendar/', include('calendarapp.urls')),
    path('menu/', include('menuapp.urls')),
    path('employees/', include('employees.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('expenses/', include('expenses.urls')),
    path('stats/', include('stats.urls')),
    path('settings/', include('settingsapp.urls')),
    path('tasks/', include('taskapp.urls')),


    # Админка существует, но ссылку в шапке мы НЕ показываем
    path('admin/', admin.site.urls),
]

```


---
## banketpro\wsgi.py
```py
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banketpro.settings')
application = get_wsgi_application()

```


---
## banketpro\__init__.py
```py

```


---
## calendarapp\apps.py
```py
from django.apps import AppConfig


class CalendarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarapp'
    verbose_name = 'Календарь и мероприятия'

    def ready(self):
        # импортируем signals, чтобы Django их «зарегистрировал»
        import calendarapp.signals  # noqa

```


---
## calendarapp\models.py
```py
from django.db import models
from crm.models import Client
from django.conf import settings

class Hall(models.Model):
    name = models.CharField('Название зала', max_length=200)
    capacity = models.PositiveIntegerField('Вместимость', default=0)

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

    def __str__(self):
        return self.name


class Event(models.Model):
    SLOT_CHOICES = [
        ('am', 'День'),
        ('pm', 'Вечер'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'В работе'),
        ('confirmed', 'Подтверждено'),
        ('paid', 'Оплачено'),
        ('canceled', 'Отменено'),
    ]

    client  = models.ForeignKey('crm.Client', on_delete=models.PROTECT, related_name='events', verbose_name='Клиент')
    hall    = models.ForeignKey('calendarapp.Hall', on_delete=models.PROTECT, verbose_name='Зал')
    date    = models.DateField('Дата')
    slot    = models.CharField('Время', max_length=2, choices=SLOT_CHOICES)
    title   = models.CharField('Название/повод', max_length=200, blank=True)
    status  = models.CharField('Статус', max_length=12, choices=STATUS_CHOICES, default='draft')

    guests  = models.PositiveIntegerField('Количество гостей', default=0)
    client_menu = models.ForeignKey('menuapp.ClientMenu', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Меню')
    extras  = models.ManyToManyField('menuapp.ExtraService', blank=True, verbose_name='Доп. услуги')
    contract= models.FileField('Договор', upload_to='contracts/', blank=True)
    prepayment_amount = models.DecimalField('Предоплата, ₽', max_digits=12, decimal_places=2, default=0)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ответственный')

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        constraints = [
            models.UniqueConstraint(fields=['hall','date','slot'], name='unique_hall_date_slot')
        ]

    def __str__(self):
        return f"{self.date} • {self.get_slot_display()} • {self.hall}"
```


---
## calendarapp\signals.py
```py
# calendarapp/signals.py
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Event

# ===== 1) Запоминаем старый статус ДО сохранения =====
@receiver(pre_save, sender=Event)
def remember_old_status(sender, instance: Event, **kwargs):
    """
    Сохраняем прошлый статус до сохранения, чтобы в post_save понять факт смены.
    """
    if instance.pk:
        try:
            old = Event.objects.only('status').get(pk=instance.pk)
            instance._old_status = old.status
        except Event.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# ===== 2) После сохранения: автосоздание меню при confirmed =====
@receiver(post_save, sender=Event)
def auto_menu_on_confirmed(sender, instance: Event, created, **kwargs):
    """
    Если статус сменился на 'confirmed' и меню не привязано — создать пустое клиентское меню.
    """
    old_status = getattr(instance, '_old_status', None)
    if instance.status == 'confirmed' and old_status != 'confirmed' and not instance.client_menu:
        from menuapp.models import ClientMenu
        title = f"Меню {instance.date:%d.%m.%Y}"
        cm = ClientMenu.objects.create(client=instance.client, title=title)
        # Привязываем без изменения других полей
        instance.client_menu = cm
        instance.save(update_fields=['client_menu'])


# ===== 3) После сохранения: списание по ТТК при paid =====
@receiver(post_save, sender=Event)
def writeoff_on_paid(sender, instance: Event, created, **kwargs):
    """
    Если статус сменился на 'paid' и есть клиентское меню — списываем продукты по ТТК:
    need = qty_на_блюдо × кол-во гостей × (1 + потери/100)
    """
    old_status = getattr(instance, '_old_status', None)
    if instance.status != 'paid' or old_status == 'paid':
        return
    if not instance.client_menu or not instance.guests:
        return

    guests = Decimal(instance.guests)
    dishes = instance.client_menu.dishes.select_related('techcard').all()

    for dish in dishes:
        tech = getattr(dish, 'techcard', None)
        if not tech:
            continue
        for ing in tech.ingredients.select_related('product').all():
            base = Decimal(ing.qty or 0)
            loss = Decimal(ing.loss_percent or 0) / Decimal(100)
            need = (base * guests) * (Decimal(1) + loss)

            product = getattr(ing, 'product', None)
            if product is None:
                continue
            if product.stock_qty is None:
                product.stock_qty = Decimal('0')
            product.stock_qty = product.stock_qty - need
            if product.stock_qty < 0:
                product.stock_qty = Decimal('0')
            product.save(update_fields=['stock_qty'])

```


---
## calendarapp\urls.py
```py
from django.urls import path
from . import views
app_name = 'calendarapp'
urlpatterns = [
    path('add/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
]

```


---
## calendarapp\views.py
```py
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

```


---
## calendarapp\__init__.py
```py

```


---
## crm\models.py
```py
from django.db import models

class Client(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=50)
    description = models.TextField('Описание', blank=True)
    source = models.CharField('Источник', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.full_name

```


---
## crm\urls.py
```py
from django.urls import path
from . import views

app_name = 'crm'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/new/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),

    path('clients/search', views.clients_search, name='client_search'),
]

```


---
## crm\views.py
```py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date, timedelta
from calendar import monthrange
from .models import Client
from calendarapp.models import Event
from django.http import JsonResponse


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


```


---
## crm\__init__.py
```py

```


---
## dump_repo.py
```py
#!/usr/bin/env python3
# dump_repo.py — собирает важные файлы в один markdown для ревью
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT  = ROOT / "repo_dump.md"

# Что включаем
INCLUDE_EXT  = {".py", ".html", ".txt", ".md", ".ini", ".cfg", ".toml", ".yaml", ".yml"}
INCLUDE_DIRS = {"banketpro", "calendarapp", "crm", "menuapp", "tasksapp",
                "warehouse", "employees", "expenses", "reviews", "settingsapp",
                "templates"}  # добавь свои app'ы при необходимости

# Что исключаем
EXCLUDE_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
                "venv", ".venv", "env", "node_modules", "static", "media",
                "migrations", "dist", "build", ".idea", ".vscode", ".DS_Store"}

def should_skip_dir(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIRS: return True
    if name.startswith('.'): return True
    return False

def should_take_file(path: Path) -> bool:
    if path.suffix.lower() not in INCLUDE_EXT: return False
    return True

def walk_selected(root: Path):
    # Ищем только внутри INCLUDE_DIRS (и корневые конфиги)
    for p in sorted(root.iterdir()):
        if p.is_file() and should_take_file(p):
            yield p
        elif p.is_dir() and (p.name in INCLUDE_DIRS) and not should_skip_dir(p):
            for sub, _, files in os.walk(p):
                sp = Path(sub)
                # отбрасываем запрещённые каталоги
                parts = set(sp.parts)
                if any(d in parts for d in EXCLUDE_DIRS): continue
                for f in files:
                    fp = sp / f
                    if should_take_file(fp):
                        yield fp

def main():
    lines = []
    lines.append("# Repository dump\n")
    for file in walk_selected(ROOT):
        rel = file.relative_to(ROOT)
        try:
            content = file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            continue
        # слегка маскируем секреты в .env и settings
        if rel.name.lower().startswith(".env") or rel.name.lower() in {"settings.py",}:
            content = re.sub(r"(SECRET_KEY\s*=\s*['\"].+?['\"])", r"SECRET_KEY = '***'", content)
            content = re.sub(r"(DATABASES\s*=\s*\{[\s\S]+?\})", r"DATABASES = { /* redacted for dump */ }", content)

        lines.append(f"\n\n---\n## {rel}\n```{file.suffix[1:] or ''}\n{content}\n```\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Written: {OUT}")

if __name__ == "__main__":
    main()

```


---
## employees\models.py
```py
from django.db import models


class Employee(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    position = models.CharField('Должность', max_length=100, blank=True)
    hourly_rate = models.DecimalField('Ставка/час', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('Категория', max_length=100, blank=True)
    contract = models.FileField('Договор', upload_to='employees/contracts/', blank=True, null=True)
    passport = models.FileField('Паспорт', upload_to='employees/passports/', blank=True, null=True)
    med_book = models.FileField('Мед. книжка', upload_to='employees/med/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Timesheet(models.Model):
    week_start = models.DateField('Начало недели (Пн)')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timesheets')

    class Meta:
        unique_together = ('week_start', 'employee')


class TimesheetEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class PayrollSettings(models.Model):
    kitchen_percent = models.DecimalField('Кухня, %', max_digits=5, decimal_places=2, default=4)
    service_percent = models.DecimalField('Сервис, %', max_digits=5, decimal_places=2, default=6)

```


---
## employees\urls.py
```py
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
  path('', views.EmployeeListView.as_view(), name='employee_list'),
  path('new/', views.EmployeeCreateView.as_view(), name='employee_create'),
  path('timesheet/', views.TimesheetWeekView.as_view(), name='timesheet_week'),
  path('payroll/', views.PayrollCalcView.as_view(), name='payroll_calc'),
]

```


---
## employees\views.py
```py
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

```


---
## employees\__init__.py
```py

```


---
## expenses\admin.py
```py
from django.contrib import admin

# Register your models here.

```


---
## expenses\apps.py
```py
from django.apps import AppConfig


class ExpensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expenses'

```


---
## expenses\forms.py
```py
from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date','type','amount','note']
        widgets = {'date': forms.DateInput(attrs={'type':'date'})}

```


---
## expenses\models.py
```py
from django.db import models

class Expense(models.Model):
    TYPES = [('хоз','Хоз'),('аренда','Аренда'),('комм','Коммуналка'),('ремонт','Ремонт'),
             ('реклама','Реклама'),('обслуж','Обслуживание'),('др','Другое')]
    date = models.DateField('Дата')
    type = models.CharField('Тип', max_length=10, choices=TYPES)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    note = models.CharField('Комментарий', max_length=200, blank=True)

    class Meta: ordering = ['-date', '-id']
    def __str__(self): return f"{self.date} • {self.get_type_display()} • {self.amount}"

```


---
## expenses\tests.py
```py
from django.test import TestCase

# Create your tests here.

```


---
## expenses\urls.py
```py
from django.urls import path
from . import views

app_name = 'expenses'
urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='expense_list'),
    path('new/', views.ExpenseCreateView.as_view(), name='expense_create'),
]

```


---
## expenses\views.py
```py
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

```


---
## expenses\__init__.py
```py

```


---
## manage.py
```py
#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banketpro.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()

```


---
## menuapp\models.py
```py
from django.db import models
from crm.models import Client
from warehouse.models import TechCard


class DishGroup(models.Model):
    name = models.CharField('Группа', max_length=100)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField('Название', max_length=200)
    photo = models.ImageField('Фото', upload_to='dishes/', blank=True, null=True)
    composition = models.TextField('Описание', blank=True)
    serving_weight = models.PositiveIntegerField('Порция, г', default=0)
    group = models.ForeignKey(DishGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name='dishes')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, default=0)
    techcard = models.ForeignKey(TechCard, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class ClientMenu(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='menus')
    title = models.CharField('Название меню', max_length=200)
    dishes = models.ManyToManyField(Dish, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.client})"

class ExtraService(models.Model):
    name = models.CharField('Услуга', max_length=200, unique=True)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, default=0)
    def __str__(self): return self.name

```


---
## menuapp\urls.py
```py
from django.urls import path
from . import views
app_name='menuapp'
urlpatterns = [
  path('', views.DishListView.as_view(), name='dish_list'),
  path('new/', views.DishCreateView.as_view(), name='dish_create'),
  path('groups/new/', views.DishGroupCreateView.as_view(), name='dishgroup_create'),
  path('clientmenu/new/', views.ClientMenuCreateView.as_view(), name='clientmenu_create'),
  path('extras/', views.ExtraServiceListView.as_view(), name='extras_list'),
  path('extras/new/', views.ExtraServiceCreateView.as_view(), name='extras_create'),
]

```


---
## menuapp\views.py
```py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import DishGroup, Dish, ClientMenu, ExtraService

class DishListView(LoginRequiredMixin, generic.ListView):
    model = Dish
    template_name = 'menu/dish_list.html'

class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    fields = ['name','photo','composition','serving_weight','group','price','techcard']
    template_name = 'menu/dish_form.html'
    success_url = '/menu/'


class DishGroupCreateView(LoginRequiredMixin, generic.CreateView):
    model = DishGroup
    fields = ['name']
    template_name = 'menu/dishgroup_form.html'
    success_url = '/menu/'

class ClientMenuCreateView(LoginRequiredMixin, generic.CreateView):
    model = ClientMenu
    fields = ['client','title','dishes']
    template_name = 'menu/clientmenu_form.html'
    success_url = '/menu/'

class ExtraServiceListView(LoginRequiredMixin, generic.ListView):
    model = ExtraService
    template_name = 'menu/extras_list.html'

class ExtraServiceCreateView(LoginRequiredMixin, generic.CreateView):
    model = ExtraService
    fields = ['name','price']
    template_name = 'menu/extras_form.html'
    success_url = '/menu/extras/'
```


---
## menuapp\__init__.py
```py

```


---
## readme.md
```md
Требования:

Python 3.12.x (проверено на 3.12.3)

Django=5.2.6


```


---
## requirements.txt
```txt
Django>=5.2.6
python-decouple
whitenoise
Pillow

```


---
## settingsapp\admin.py
```py
from django.contrib import admin

# Register your models here.

```


---
## settingsapp\apps.py
```py
from django.apps import AppConfig


class SettingsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settingsapp'

```


---
## settingsapp\forms.py
```py
from django import forms
from calendarapp.models import Hall
from employees.models import PayrollSettings

class HallForm(forms.ModelForm):
    class Meta: model = Hall; fields = ['name']

class PayrollSettingsForm(forms.ModelForm):
    class Meta: model = PayrollSettings; fields = ['kitchen_percent','service_percent']

```


---
## settingsapp\models.py
```py
from django.db import models

# Create your models here.

```


---
## settingsapp\tests.py
```py
from django.test import TestCase

# Create your tests here.

```


---
## settingsapp\urls.py
```py
from django.urls import path
from .views import SettingsHomeView, HallListView, HallCreateView, PayrollSettingsView

app_name='settingsapp'
urlpatterns = [
    path('', SettingsHomeView.as_view(), name='home'),
    path('halls/', HallListView.as_view(), name='hall_list'),
    path('halls/new/', HallCreateView.as_view(), name='hall_create'),
    path('payroll/', PayrollSettingsView.as_view(), name='payroll'),
]

```


---
## settingsapp\views.py
```py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import redirect
from calendarapp.models import Hall
from employees.models import PayrollSettings
from .forms import HallForm, PayrollSettingsForm

class SettingsHomeView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'settingsapp/home.html'

class HallListView(LoginRequiredMixin, generic.ListView):
    model = Hall; template_name = 'settingsapp/hall_list.html'

class HallCreateView(LoginRequiredMixin, generic.CreateView):
    model = Hall; form_class = HallForm
    template_name = 'settingsapp/hall_form.html'; success_url = '/settings/halls/'

class PayrollSettingsView(LoginRequiredMixin, generic.FormView):
    template_name = 'settingsapp/payroll_form.html'; form_class = PayrollSettingsForm
    success_url = '/settings/payroll/'
    def get_initial(self):
        ps, _ = PayrollSettings.objects.get_or_create(pk=1)
        return {'kitchen_percent': ps.kitchen_percent, 'service_percent': ps.service_percent}
    def form_valid(self, form):
        ps, _ = PayrollSettings.objects.get_or_create(pk=1)
        ps.kitchen_percent = form.cleaned_data['kitchen_percent']
        ps.service_percent = form.cleaned_data['service_percent']
        ps.save()
        return super().form_valid(form)

```


---
## settingsapp\__init__.py
```py

```


---
## templates\base.html
```html
{% load static %}
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{% block title %}BanketPro{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{% static 'css/app.css' %}" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
  <div class="container">
    <a class="navbar-brand fw-semibold text-primary" href="/">BanketPro</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="nav">
      <ul class="navbar-nav me-auto">
          <li class="nav-item"><a class="nav-link" href="{% url 'crm:dashboard' %}">Дашборд</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'crm:client_list' %}">Клиенты</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'menuapp:dish_list' %}">Меню</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'employees:employee_list' %}">Сотрудники</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'warehouse:product_list' %}">Склад</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'expenses:expense_list' %}">Расходы</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'settingsapp:home' %}">Настройки</a></li>
      </ul>
        <div class="d-flex">
          {% if user.is_authenticated %}
            <span class="me-3 small text-muted">{{ user.username }}</span>
            <a class="btn btn-sm btn-outline-secondary" href="{% url 'logout' %}">Выйти</a>
          {% else %}
            <a class="btn btn-sm btn-primary" href="{% url 'login' %}">Войти</a>
          {% endif %}
        </div>
    </div>
  </div>
</nav>
<main class="container py-4">
  {% if messages %}
    <div class="mb-3">
      {% for m in messages %}
        <div class="alert alert-{{ m.tags|default:'secondary' }} mb-2" role="alert">{{ m }}</div>
      {% endfor %}
    </div>
  {% endif %}
  {% block content %}{% endblock %}
</main>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

```


---
## templates\landing.html
```html
{% extends 'base.html' %}
{% block title %}BanketPro — CRM для банкетов{% endblock %}
{% block content %}
<div class="row align-items-center g-4">
  <div class="col-lg-7">
    <h1 class="display-6 fw-bold">CRM для банкетных залов</h1>
    <p class="lead text-muted">Календарь с половинками дня, клиенты, задачи и меню — всё, чтобы быстро бронировать и вести заказы.</p>
    <a class="btn btn-primary btn-lg" href="/accounts/login/">Перейти в личный кабинет</a>
  </div>
  <div class="col-lg-5">
    <div class="p-4 bg-white border rounded-4 shadow-sm">
      <h2 class="h5">Возможности</h2>
      <ul class="small">
        <li>Интерактивный календарь: утро/вечер/полный день</li>
        <li>Клиенты и меню</li>
        <li>Предоплаты и статусы</li>
      </ul>
    </div>
  </div>
</div>
{% endblock %}

```


---
## templates\calendar\event_detail.html
```html
{% extends 'base.html' %}
{% block title %}Мероприятие {{ object.date|date:"d.m.Y" }}{% endblock %}
{% block content %}

<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h5 m-0">Мероприятие: {{ object.date|date:"d.m.Y" }} • {{ object.get_slot_display }} • {{ object.hall }}</h1>
  <a class="btn btn-outline-secondary btn-sm" href="{% url 'crm:dashboard' %}">К дашборду</a>
</div>

<div class="row g-3">
  <div class="col-md-5">
    <div class="card p-3 shadow-sm">
      <div class="small text-muted mb-2">Клиент и параметры</div>
      <div><strong>{{ object.client.full_name }}</strong> — <a href="tel:{{ object.client.phone }}">{{ object.client.phone }}</a></div>
      <div class="text-muted small mt-2">Зал: {{ object.hall }}</div>
      <div class="text-muted small">Гостей: {{ object.guests }}</div>
      <div class="text-muted small">Статус: {{ object.get_status_display }}</div>
      <div class="text-muted small">Предоплата: {{ object.prepayment_amount|default:"0" }}</div>
      <div class="text-muted small">Меню: {% if object.client_menu %}{{ object.client_menu.title }}{% else %}—{% endif %}</div>
      <div class="text-muted small">Доп.услуги:
        {% for e in object.extras.all %}{{ e.name }}{% if not forloop.last %}, {% endif %}{% empty %}—{% endfor %}
      </div>
      {% if object.contract %}
        <div class="small mt-2"><a href="{{ object.contract.url }}" target="_blank">Договор</a></div>
      {% endif %}
    </div>
  </div>

  <div class="col-md-7">
    <div class="card p-3 shadow-sm">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <div class="small text-muted">Задачи</div>
        <a class="btn btn-sm btn-primary" href="{% url 'tasksapp:event_task_create' object.pk %}">+ Задача</a>
      </div>
      {% include "tasks/_task_inline_list.html" with tasks=object.tasks.all only %}
    </div>
  </div>
</div>

{% endblock %}

```


---
## templates\calendar\event_form.html
```html
{% extends 'base.html' %}
{% block title %}Новое мероприятие{% endblock %}
{% block content %}
<h1 class="h5 mb-3">Добавить мероприятие</h1>
<form method="post" enctype="multipart/form-data" class="card p-3 shadow-sm">{% csrf_token %}
  <div class="row g-3">
    <div class="col-12">
      <div class="form-check form-switch">
        {{ form.new_client }} <label class="form-check-label" for="{{ form.new_client.id_for_label }}">Создать нового клиента</label>
      </div>
    </div>

    <div id="block-existing" class="col-md-6">
      <label class="form-label">Клиент (поиск)</label>
      <input type="text" class="form-control" id="clientSearch" placeholder="ФИО или телефон">
      {{ form.client }}
    </div>

    <div id="block-new" class="col-12 row g-3" style="display:none">
      <div class="col-md-6">{{ form.new_full_name.label_tag }} {{ form.new_full_name }}</div>
      <div class="col-md-6">{{ form.new_phone.label_tag }} {{ form.new_phone }}</div>
      <div class="col-md-6">{{ form.new_source.label_tag }} {{ form.new_source }}</div>
      <div class="col-12">{{ form.new_description.label_tag }} {{ form.new_description }}</div>
    </div>

    <div class="col-md-4">{{ form.date.label_tag }} {{ form.date }}</div>
    <div class="col-md-4">{{ form.slot.label_tag }} {{ form.slot }}</div>
    <div class="col-md-4">{{ form.slot_full }} {{ form.slot_full.label_tag }}</div>

    <div class="col-md-6">{{ form.hall.label_tag }} {{ form.hall }}</div>
    <div class="col-md-6">{{ form.title.label_tag }} {{ form.title }}</div>

    <div class="col-md-4">{{ form.guests.label_tag }} {{ form.guests }}</div>
    <div class="col-md-4">{{ form.client_menu.label_tag }} {{ form.client_menu }}</div>
    <div class="col-md-4">{{ form.extras.label_tag }} {{ form.extras }}</div>

    <div class="col-md-6">{{ form.prepayment_amount.label_tag }} {{ form.prepayment_amount }}</div>
    <div class="col-md-6">{{ form.status.label_tag }} {{ form.status }}</div>

    <div class="col-md-6">{{ form.contract.label_tag }} {{ form.contract }}</div>
    <div class="col-md-6">{{ form.responsible.label_tag }} {{ form.responsible }}</div>
  </div>

  <div class="mt-3 d-flex gap-2">
    <button class="btn btn-primary">Сохранить</button>
    <a class="btn btn-outline-secondary" href="{% url 'crm:dashboard' %}">Отмена</a>
  </div>
</form>

<script>
const blockNew = document.getElementById('block-new');
const blockExist = document.getElementById('block-existing');
function toggleNew(){ const on = document.querySelector('[name="new_client"]').checked; blockNew.style.display = on?'':'none'; blockExist.style.display = on?'none':''; }
document.querySelector('[name="new_client"]').addEventListener('change', toggleNew); toggleNew();

const input = document.getElementById('clientSearch'); const select = document.getElementById('id_client');
if (input){
  let t=null;
  input.addEventListener('input', ()=>{
    clearTimeout(t);
    t = setTimeout(async ()=>{
      const q = input.value.trim(); if(!q){ return; }
      const r = await fetch(`/crm/clients/search?q=${encodeURIComponent(q)}`);
      const items = await r.json(); select.innerHTML = '';
      items.forEach(it=>{
        const opt = document.createElement('option');
        opt.value = it.id; opt.textContent = `${it.full_name} — ${it.phone}`;
        select.appendChild(opt);
      });
    }, 250);
  });
}
</script>
{% endblock %}

```


---
## templates\crm\client_detail.html
```html
{% extends 'base.html' %}
{% block title %}Клиент {{ object.full_name }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h5 m-0">Клиент: {{ object.full_name }}</h1>
  <div>
    <a class="btn btn-outline-primary btn-sm" href="{% url 'crm:client_update' object.pk %}">Редактировать</a>
  </div>
</div>

<div class="row g-3">
  <div class="col-md-4">
    <div class="card p-3 shadow-sm">
      <div class="small text-muted mb-2">Контакты</div>
      <div><strong>Телефон:</strong> <a href="tel:{{ object.phone }}">{{ object.phone|default:"—" }}</a></div>
      <div><strong>Источник:</strong> {{ object.source|default:"—" }}</div>
      <div><strong>Описание:</strong> {{ object.description|default:"—" }}</div>
      <div class="text-muted small mt-2">Создан: {{ object.created_at|date:"d.m.Y H:i" }}</div>
    </div>
    <div class="card p-3 shadow-sm mt-3">
      <div class="small text-muted mb-2">Действия</div>
      <a class="btn btn-primary w-100" href="{% url 'calendarapp:event_create' %}?client={{ object.pk }}">+ Добавить мероприятие</a>
    </div>
  </div>
  <div class="col-md-8">
    <div class="card p-3 shadow-sm">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <div class="small text-muted">Мероприятия клиента</div>
      </div>
      <table class="table table-sm align-middle">
        <thead><tr><th>Дата</th><th>Слот</th><th>Зал</th><th>Статус</th><th>Предоплата</th></tr></thead>
        <tbody>
          {% for e in events %}
          <tr>
                <td><a href="{% url 'calendarapp:event_detail' e.pk %}">{{ e.date|date:"d.m.Y" }}</a></td>
                <td><a href="{% url 'calendarapp:event_detail' e.pk %}">{{ e.get_slot_display }}</a></td>
                <td>{{ e.hall }}</td>
                <td><span class="badge bg-secondary">{{ e.get_status_display }}</span></td>
                <td>{{ e.prepayment_amount|default:"0" }}</td>
              </tr>
                {% empty %}
              <tr><td colspan="5" class="text-muted">Нет мероприятий</td></tr>
         {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>

{% endblock %}

```


---
## templates\crm\client_form.html
```html
{% extends 'base.html' %}
{% block title %}Клиент{% endblock %}
{% block content %}
<h1 class="h5 mb-3">{% if object %}Редактировать{% else %}Добавить{% endif %} клиента</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}
  <div class="row g-3">
    <div class="col-md-6">{{ form.full_name.label_tag }} {{ form.full_name }}</div>
    <div class="col-md-6">{{ form.phone.label_tag }} {{ form.phone }}</div>
    <div class="col-md-6">{{ form.source.label_tag }} {{ form.source }}</div>
    <div class="col-12">{{ form.description.label_tag }} {{ form.description }}</div>
  </div>
  <div class="mt-3 d-flex gap-2">
    <button class="btn btn-primary">Сохранить</button>
    <a class="btn btn-outline-secondary" href="{% url 'crm:client_list' %}">Отмена</a>
  </div>
</form>
{% endblock %}

```


---
## templates\crm\client_list.html
```html
{% extends 'base.html' %}
{% block title %}Клиенты{% endblock %}
{% block content %}
<h1 class="h4 mb-3">Клиенты</h1>

<form class="row g-2 mb-3" method="get">
  <div class="col-12 col-md-3">
    <input class="form-control" name="q" placeholder="ФИО / телефон" value="{{ request.GET.q }}">
  </div>
  <div class="col-12 col-md-3">
    <input class="form-control" type="date" name="event_date" value="{{ request.GET.event_date }}" placeholder="Дата мероприятия">
  </div>
  <div class="col-12 col-md-2">
    <button class="btn btn-outline-secondary w-100">Искать</button>
  </div>
  <div class="col-12 col-md-4 text-md-end">
    <a class="btn btn-primary" href="{% url 'crm:client_create' %}">+ Добавить клиента</a>
  </div>
</form>

<table class="table table-sm align-middle bg-white">
  <thead>
    <tr>
      <th>ФИО</th>
      <th>Телефон</th>
      <th>Источник</th>
      <th>Создан</th>
      <th class="text-end">Мероприятий</th>
    </tr>
  </thead>
  <tbody>
    {% for c in object_list %}
      <tr>
        <td><a href="{% url 'crm:client_detail' c.pk %}">{{ c.full_name }}</a></td>
        <td><a href="tel:{{ c.phone }}">{{ c.phone }}</a></td>
        <td>{{ c.source|default:"—" }}</td>
        <td>{{ c.created_at|date:"d.m.Y H:i" }}</td>
        <td class="text-end">{{ c.event_count|default:"0" }}</td>
      </tr>
    {% empty %}
      <tr><td colspan="5" class="text-muted">Нет клиентов</td></tr>
    {% endfor %}
  </tbody>
</table>

{% include "_partials/pagination.html" with page_obj=page_obj %}
{% endblock %}

```


---
## templates\crm\dashboard.html
```html
{% extends 'base.html' %}
{% block title %}Рабочий стол • BanketPro{% endblock %}
{% block content %}
<div class="d-flex align-items-center justify-content-between mb-3">
  <h1 class="h4 m-0">Рабочий стол</h1>
  <div class="d-flex gap-2">
    <a class="btn btn-outline-primary" href="{% url 'crm:client_create' %}">+ Добавить клиента</a>
    <a class="btn btn-primary" href="{% url 'calendarapp:event_create' %}">+ Добавить мероприятие</a>
  </div>
</div>


<div class="card shadow-sm mb-3">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <div class="btn-group" role="group">
        <a class="btn btn-sm btn-outline-secondary" href="?year={{ prev_year }}&month={{ prev_month }}">«</a>
        <span class="btn btn-sm btn-outline-secondary disabled">{{ year }} / {{ month }}</span>
        <a class="btn btn-sm btn-outline-secondary" href="?year={{ next_year }}&month={{ next_month }}">»</a>
      </div>
    </div>

    <div class="row row-cols-7 g-2 mb-1">
      <div class="col text-center small text-muted">Пн</div>
      <div class="col text-center small text-muted">Вт</div>
      <div class="col text-center small text-muted">Ср</div>
      <div class="col text-center small text-muted">Чт</div>
      <div class="col text-center small text-muted">Пт</div>
      <div class="col text-center small text-muted">Сб</div>
      <div class="col text-center small text-muted">Вс</div>
    </div>

    {% for week in weeks %}
      <div class="row row-cols-7 g-2 mb-2">
        {% for cell in week %}
          <div class="col">
            {% if cell.blank %}
              <div class="cal-cell cal-empty"></div>
            {% else %}
              <div class="cal-cell" data-date="{{ cell.date_str }}">
                <div class="d-flex justify-content-between">
                  <div class="small fw-semibold">{{ cell.n }}</div>
                  <div class="slot-dot" data-am="{{ cell.am|yesno:'1,0' }}" data-pm="{{ cell.pm|yesno:'1,0' }}"></div>
                </div>
                {% if cell.am or cell.pm %}
                  {% if cell.am %}<div class="small text-truncate mt-1">Утро: {{ cell.am.client.full_name }}</div>{% endif %}
                  {% if cell.pm %}<div class="small text-truncate">Вечер: {{ cell.pm.client.full_name }}</div>{% endif %}
                {% else %}
                  <button class="add-btn" type="button" title="Добавить" data-date="{{ cell.date_str }}">+</button>
                {% endif %}
              </div>
            {% endif %}
          </div>
        {% endfor %}
      </div>
    {% endfor %}
  </div>
</div>

<div class="card shadow-sm">
  <div class="card-body">
    <div class="d-flex justify-content-between"><div class="text-muted small">Выручка за месяц</div><span class="badge bg-success">₽</span></div>
    <div class="display-6 fw-semibold mt-2">{{ revenue|default:0 }}</div>
  </div>
</div>

<!-- Modal slot chooser -->
<div class="modal fade" id="slotModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog"><div class="modal-content">
    <div class="modal-header">
      <h5 class="modal-title">На какое время записать?</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body">
      <div class="d-grid gap-2">
        <a class="btn btn-outline-primary" id="choose-am">День</a>
        <a class="btn btn-outline-success" id="choose-pm">Вечер</a>
        <a class="btn btn-primary" id="choose-full">Полный день</a>
      </div>
    </div>
  </div></div>
</div>

<style>
.cal-cell { position:relative; border:1px solid #eee; border-radius:.5rem; padding:.5rem; min-height:100px; background:#fff; overflow:hidden }
.cal-empty { min-height:100px; border:1px dashed #eee; border-radius:.5rem; background:#fafafa }
.slot-dot { width:16px; height:16px; border-radius:50%; border:1px solid #ced4da }
.slot-dot[data-am='1'][data-pm='0'] { background: linear-gradient(to right, var(--bs-primary) 50%, transparent 50%) }
.slot-dot[data-am='0'][data-pm='1'] { background: linear-gradient(to right, transparent 50%, var(--bs-success) 50%) }
.slot-dot[data-am='1'][data-pm='1'] { background: linear-gradient(to right, var(--bs-primary) 50%, var(--bs-success) 50%); border-color: var(--bs-success) }
/* "+" виден только при наведении на пустую ячейку */
.add-btn { position:absolute; right:.4rem; bottom:.4rem; width:28px; height:28px; border-radius:50%; border:0; opacity:0; transition:opacity .15s; font-weight:700; line-height:1; background:#6f42c1; color:#fff }
.cal-cell:hover .add-btn { opacity:1 }
</style>

<script>
(function(){
  let selectedDate = null;
  document.addEventListener('click', function(e){
    if (e.target.matches('.add-btn')){
      selectedDate = e.target.dataset.date;
      const m = new bootstrap.Modal(document.getElementById('slotModal')); m.show();
    }
    if (e.target.matches('#choose-am')){
      window.location.href = "{% url 'calendarapp:event_create' %}" + "?date=" + selectedDate + "&slot=am";
    }
    if (e.target.matches('#choose-pm')){
      window.location.href = "{% url 'calendarapp:event_create' %}" + "?date=" + selectedDate + "&slot=pm";
    }
    if (e.target.matches('#choose-full')){
      window.location.href = "{% url 'calendarapp:event_create' %}" + "?date=" + selectedDate + "&slot=full";
    }
  }, false);
})();
</script>

    <div class="card shadow-sm mt-3">
      <div class="card-body">
        <h2 class="h6 mb-3">Ближайшие 7 дней</h2>
        <ul class="list-group list-group-flush">
          {% for ev in upcoming_week %}
            <li class="list-group-item d-flex justify-content-between">
              <span><strong>{{ ev.date|date:"d.m.Y" }}</strong> • {{ ev.get_slot_display }} • {{ ev.hall }} — {{ ev.client.full_name }}</span>
              <span class="badge bg-secondary">{{ ev.get_status_display }}</span>
            </li>
          {% empty %}
            <li class="list-group-item text-muted">Нет ближайших мероприятий</li>
          {% endfor %}
        </ul>
      </div>
    </div>

{% endblock %}

```


---
## templates\employees\employee_form.html
```html
{% extends 'base.html' %}{% block title %}Новый сотрудник{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить сотрудника</h1>
<form method="post" enctype="multipart/form-data" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <div class="mt-2"><button class="btn btn-primary">Сохранить</button></div>
</form>{% endblock %}

```


---
## templates\employees\employee_list.html
```html
{% extends 'base.html' %}
{% block title %}Сотрудники{% endblock %}
{% block content %}
<h1 class="h4 mb-3">Сотрудники</h1>
<div class="mb-3 d-flex gap-2">
  <a class="btn btn-primary" href="{% url 'employees:employee_create' %}">+ Добавить сотрудника</a>
  <a class="btn btn-outline-secondary" href="{% url 'employees:timesheet_week' %}">Табель (неделя)</a>
  <a class="btn btn-outline-secondary" href="{% url 'employees:payroll_calc' %}">Расчёт ЗП</a>
</div>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>ФИО</th><th>Телефон</th><th>Должность</th><th class="text-end">Ставка/час</th></tr></thead>
  <tbody>
    {% for e in object_list %}
      <tr>
        <td>{{ e.full_name }}</td>
        <td><a href="tel:{{ e.phone }}">{{ e.phone }}</a></td>
        <td>{{ e.position|default:"—" }}</td>
        <td class="text-end">{{ e.hourly_rate|default:"0" }}</td>
      </tr>
    {% empty %}
      <tr><td colspan="4" class="text-muted">Нет сотрудников</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}

```


---
## templates\employees\payroll_calc.html
```html
{% extends 'base.html' %}
{% block title %}Расчёт ЗП{% endblock %}
{% block content %}
<h1 class="h4 mb-3">Расчёт зарплаты</h1>
<div class="row g-3">
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="small text-muted">Выручка</div><div class="h4 m-0">{{ revenue }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="small text-muted">Кухня ({{ settings.kitchen_percent }}%)</div><div class="h4 m-0">{{ kitchen }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="small text-muted">Сервис ({{ settings.service_percent }}%)</div><div class="h4 m-0">{{ service }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="small text-muted">Итого ФОТ</div><div class="h4 m-0">{{ kitchen|add:service }}</div></div></div>
</div>
{% endblock %}

```


---
## templates\employees\timesheet_week.html
```html
{% extends 'base.html' %}
{% block title %}Табель — неделя{% endblock %}
{% block content %}
<h1 class="h5 mb-3">Табель — неделя {{ week_start|date:"d.m.Y" }}–{{ week_end|date:"d.m.Y" }}</h1>

<form method="get" class="row g-2 mb-3">
  <div class="col-auto">
    <input type="date" class="form-control" name="week" value="{{ request.GET.week }}">
  </div>
  <div class="col-auto">
    <button class="btn btn-outline-secondary">Показать</button>
  </div>
</form>

<form method="post" class="card p-3 shadow-sm">{% csrf_token %}
  <div class="table-responsive">
    <table class="table table-sm align-middle">
      <thead>
        <tr>
          <th>Сотрудник</th>
          {% for d in days %}<th class="text-center">{{ d|date:"D d.m" }}</th>{% endfor %}
          <th class="text-end">Итого</th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
          <tr>
            <td>{{ row.employee.full_name }}</td>
            {% for cell in row.cells %}
              <td class="text-center" style="width:110px;">
                <input class="form-control form-control-sm text-center" style="max-width:90px"
                       name="hours_{{ row.employee.id }}_{{ forloop.counter0 }}" value="{{ cell.hours|default:"0" }}">
              </td>
            {% endfor %}
            <td class="text-end">{{ row.total|default:"0" }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  <div><button class="btn btn-primary">Сохранить табель</button></div>
</form>
{% endblock %}

```


---
## templates\expenses\expense_form.html
```html
{% extends 'base.html' %}{% block title %}Новый расход{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить расход</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <button class="btn btn-primary">Сохранить</button>
</form>{% endblock %}

```


---
## templates\expenses\expense_list.html
```html
{% extends 'base.html' %}{% block title %}Расходы{% endblock %}{% block content %}
<h1 class="h4 mb-3">Расходы</h1>
<form class="row g-2 mb-3">
  <div class="col-auto"><input type="date" class="form-control" name="date_from" value="{{ request.GET.date_from }}"></div>
  <div class="col-auto"><input type="date" class="form-control" name="date_to" value="{{ request.GET.date_to }}"></div>
  <div class="col-auto">
    <select name="type" class="form-select">
      <option value="">Тип</option>
      {% for k,v in object_list.model.TYPES %}<option value="{{ k }}" {% if request.GET.type == k %}selected{% endif %}>{{ v }}</option>{% endfor %}
    </select>
  </div>
  <div class="col-auto"><button class="btn btn-outline-secondary">Фильтр</button></div>
  <div class="col ms-auto text-end">
    <a class="btn btn-primary" href="{% url 'expenses:expense_create' %}">+ Добавить расход</a>
    <a class="btn btn-outline-success" href="?{% if request.META.QUERY_STRING %}{{ request.META.QUERY_STRING }}&{% endif %}export=csv">Экспорт CSV</a>
  </div>
</form>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>Дата</th><th>Тип</th><th class="text-end">Сумма</th><th>Комментарий</th></tr></thead>
  <tbody>
    {% for e in object_list %}
      <tr><td>{{ e.date|date:"d.m.Y" }}</td><td>{{ e.get_type_display }}</td><td class="text-end">{{ e.amount }}</td><td>{{ e.note }}</td></tr>
    {% empty %}
      <tr><td colspan="4" class="text-muted">Нет данных</td></tr>
    {% endfor %}
  </tbody>
  <tfoot><tr><th colspan="2">Итого</th><th class="text-end">{{ total }}</th><th></th></tr></tfoot>
</table>
{% endblock %}

```


---
## templates\menu\clientmenu_detail.html
```html
{% extends 'base.html' %}
{% block title %}Меню клиента{% endblock %}
{% block content %}
<h1 class="h5 mb-3">{{ object.title }} — {{ object.client.full_name }}</h1>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>Блюдо</th><th>Группа</th><th class="text-end">Цена</th></tr></thead>
  <tbody>
    {% for d in object.dishes.all %}
      <tr><td>{{ d.name }}</td><td>{{ d.group|default:"—" }}</td><td class="text-end">{{ d.price }}</td></tr>
    {% empty %}
      <tr><td colspan="3" class="text-muted">Меню пусто</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr><th colspan="2">Итого</th><th class="text-end">
      {{ object.dishes.all|map:'price'|sum }} {# если есть кастомный фильтр; иначе считай во view #}
    </th></tr>
  </tfoot>
</table>
{% endblock %}

```


---
## templates\menu\clientmenu_form.html
```html
{% extends 'base.html' %}{% block title %}Меню для клиента{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить меню для клиента</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <div class="mt-2"><button class="btn btn-primary">Сохранить</button></div>
</form>{% endblock %}

```


---
## templates\menu\dishgroup_form.html
```html
{% extends 'base.html' %}{% block title %}Новая группа блюд{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить группу блюд</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <div class="mt-2"><button class="btn btn-primary">Сохранить</button></div>
</form>{% endblock %}

```


---
## templates\menu\dish_form.html
```html
{% extends 'base.html' %}{% block title %}Новое блюдо{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить блюдо</h1>
<form method="post" enctype="multipart/form-data" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <div class="mt-2"><button class="btn btn-primary">Сохранить</button></div>
</form>{% endblock %}

```


---
## templates\menu\dish_list.html
```html
{% extends 'base.html' %}
{% block title %}Меню — блюда{% endblock %}
{% block content %}
<h1 class="h4 mb-3">Меню</h1>
<div class="d-flex gap-2 mb-3">
  <a class="btn btn-primary" href="{% url 'menuapp:dish_create' %}">+ Блюдо</a>
  <a class="btn btn-outline-primary" href="{% url 'menuapp:dishgroup_create' %}">+ Группа блюд</a>
  <a class="btn btn-outline-primary" href="{% url 'menuapp:clientmenu_create' %}">+ Меню для клиента</a>
</div>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>Блюдо</th><th>Группа</th><th class="text-end">Цена</th><th>ТТК</th></tr></thead>
  <tbody>
  {% for d in object_list %}
    <tr>
      <td>{{ d.name }}</td>
      <td>{{ d.group|default:"—" }}</td>
      <td class="text-end">{{ d.price|default:"0" }}</td>
      <td>{% if d.techcard %}<a href="{% url 'warehouse:techcard_detail' d.techcard.pk %}">{{ d.techcard.title }}</a>{% else %}—{% endif %}</td>
    </tr>
  {% empty %}
    <tr><td colspan="4" class="text-muted">Добавьте блюда</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}

```


---
## templates\registration\logged_out.html
```html
{% extends 'base.html' %}
{% block title %}Вы вышли • BanketPro{% endblock %}
{% block content %}
<div class="alert alert-info">Вы вышли из аккаунта. <a href="{% url 'login' %}">Войти снова</a></div>
{% endblock %}

```


---
## templates\registration\login.html
```html
{% extends 'base.html' %}
{% block title %}Войти • BanketPro{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-4">
    <div class="card shadow-sm p-3">
      <h1 class="h5 mb-3">Вход</h1>
      {% if form.errors %}
        <div class="alert alert-danger">Неверный логин или пароль.</div>
      {% endif %}
      <form method="post" action="{% url 'login' %}">{% csrf_token %}
        <div class="mb-3"><label class="form-label">Логин</label>
          <input type="text" name="username" class="form-control" required autofocus></div>
        <div class="mb-3"><label class="form-label">Пароль</label>
          <input type="password" name="password" class="form-control" required></div>
        <button class="btn btn-primary w-100" type="submit">Войти</button>
      </form>
    </div>
  </div>
</div>
{% endblock %}

```


---
## templates\settingsapp\hall_form.html
```html
{% extends 'base.html' %}{% block title %}Новый зал{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить зал</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <button class="btn btn-primary">Сохранить</button>
</form>{% endblock %}

```


---
## templates\settingsapp\hall_list.html
```html
{% extends 'base.html' %}{% block title %}Залы{% endblock %}{% block content %}
<h1 class="h4 mb-3">Залы</h1>
<div class="mb-3"><a class="btn btn-primary" href="{% url 'settingsapp:hall_create' %}">+ Зал</a></div>
<table class="table table-sm bg-white">
  <thead><tr><th>Название</th></tr></thead>
  <tbody>{% for h in object_list %}<tr><td>{{ h.name }}</td></tr>{% empty %}<tr><td class="text-muted">Пусто</td></tr>{% endfor %}</tbody>
</table>
{% endblock %}

```


---
## templates\settingsapp\home.html
```html
{% extends 'base.html' %}{% block title %}Настройки{% endblock %}{% block content %}
<h1 class="h4 mb-3">Настройки</h1>
<div class="row g-3">
  <div class="col-md-4"><a class="card p-3 shadow-sm text-decoration-none" href="{% url 'settingsapp:hall_list' %}">
    <div class="h6 m-0">Залы</div><div class="text-muted small">Справочник залов</div></a></div>
  <div class="col-md-4"><a class="card p-3 shadow-sm text-decoration-none" href="{% url 'settingsapp:payroll' %}">
    <div class="h6 m-0">Проценты ЗП</div><div class="text-muted small">Кухня/Сервис</div></a></div>
</div>
{% endblock %}

```


---
## templates\settingsapp\payroll_form.html
```html
{% extends 'base.html' %}{% block title %}Проценты ЗП{% endblock %}{% block content %}
<h1 class="h4 mb-3">Проценты ЗП</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <button class="btn btn-primary">Сохранить</button>
</form>{% endblock %}

```


---
## templates\stats\dashboard.html
```html
{% extends 'base.html' %}{% block title %}Статистика{% endblock %}{% block content %}
<h1 class="h4 mb-3">Статистика</h1>
<form class="row g-2 mb-3">
  <div class="col-auto"><input type="date" class="form-control" name="date_from" value="{{ date_from }}"></div>
  <div class="col-auto"><input type="date" class="form-control" name="date_to" value="{{ date_to }}"></div>
  <div class="col-auto"><button class="btn btn-outline-secondary">Фильтр</button></div>
</form>
<div class="row g-3">
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="text-muted small">Выручка</div><div class="h4 m-0">{{ revenue }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="text-muted small">Расходы</div><div class="h4 m-0">{{ expenses }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="text-muted small">Зарплаты (кух {{ kitchen_pct }}%, сервис {{ service_pct }}%)</div><div class="h4 m-0">{{ kitchen|add:service }}</div></div></div>
  <div class="col-md-3"><div class="card p-3 shadow-sm"><div class="text-muted small">Прибыль</div><div class="h4 m-0">{{ profit }}</div></div></div>
</div>
{% endblock %}

```


---
## templates\tasks\task_form.html
```html
{% extends 'base.html' %}
{% block title %}Новая задача{% endblock %}
{% block content %}
<h1 class="h5 mb-3">Добавить задачу</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}
  <div class="row g-3">
    <div class="col-md-4">{{ form.task_type.label_tag }} {{ form.task_type }}</div>
    <div class="col-md-8">{{ form.description.label_tag }} {{ form.description }}</div>
    <div class="col-md-4">{{ form.deadline.label_tag }} {{ form.deadline }}</div>
    <div class="col-md-4">{{ form.responsible.label_tag }} {{ form.responsible }}</div>
    <div class="col-md-4">{{ form.status.label_tag }} {{ form.status }}</div>
  </div>
  <div class="mt-3"><button class="btn btn-primary">Сохранить</button></div>
</form>
{% endblock %}

```


---
## templates\tasks\task_list.html
```html
{% extends 'base.html' %}
{% block title %}Задачи{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h5 m-0">Задачи</h1>
  <form class="d-flex gap-2" method="get">
    <select class="form-select form-select-sm" name="status">
      <option value="">Все статусы</option>
      <option value="in_progress" {% if request.GET.status == 'in_progress' %}selected{% endif %}>В работе</option>
      <option value="done" {% if request.GET.status == 'done' %}selected{% endif %}>Завершена</option>
      <option value="canceled" {% if request.GET.status == 'canceled' %}selected{% endif %}>Отменена</option>
    </select>
    <button class="btn btn-sm btn-outline-secondary">Фильтр</button>
  </form>
</div>

<ul class="list-group">
  {% for t in object_list %}
    <li class="list-group-item d-flex justify-content-between align-items-center task-{{ t.status }}">
      <div>
        <span class="badge me-2 text-bg-light">{{ t.get_task_type_display }}</span>
        {{ t.description }}
        {% if t.event %}<span class="small text-muted">по событию {{ t.event.date|date:"d.m.Y" }} {{ t.event.get_slot_display }}</span>{% endif %}
      </div>
      <div class="small text-muted">
        {% if t.responsible %}{{ t.responsible.username }} · {% endif %}
        {{ t.get_status_display }}
      </div>
    </li>
  {% empty %}
    <li class="list-group-item text-muted">Нет задач</li>
  {% endfor %}
</ul>
{% endblock %}

```


---
## templates\tasks\_task_inline_list.html
```html
<ul class="list-group list-group-flush">
  {% for t in tasks %}
    <li class="list-group-item d-flex justify-content-between align-items-center task-{{ t.status }}">
      <div>
        <span class="badge me-2 text-bg-light">{{ t.get_task_type_display }}</span>
        {{ t.description }}
        {% if t.deadline %}<span class="small text-muted">до {{ t.deadline|date:"d.m.Y H:i" }}</span>{% endif %}
      </div>
      <div class="small text-muted">
        {% if t.responsible %}{{ t.responsible.username }} · {% endif %}
        {{ t.get_status_display }}
      </div>
    </li>
  {% empty %}
    <li class="list-group-item text-muted">Задач пока нет</li>
  {% endfor %}
</ul>

<style>
.task-in_progress { border-left: 4px solid #fd7e14; }
.task-done        { border-left: 4px solid #198754; opacity:.9; }
.task-canceled    { border-left: 4px solid #dc3545; opacity:.8; }
</style>

```


---
## templates\warehouse\product_form.html
```html
{% extends 'base.html' %}{% block title %}Новый товар{% endblock %}{% block content %}
<h1 class="h4 mb-3">Добавить товар</h1>
<form method="post" class="card p-3 shadow-sm">{% csrf_token %}{{ form.as_p }}
  <button class="btn btn-primary">Сохранить</button>
</form>{% endblock %}

```


---
## templates\warehouse\product_list.html
```html
{% extends 'base.html' %}{% block title %}Склад — номенклатура{% endblock %}{% block content %}
<h1 class="h4 mb-3">Номенклатура</h1>
<form class="row g-2 mb-3">
  <div class="col-auto"><input class="form-control" name="q" placeholder="Поиск..." value="{{ request.GET.q }}"></div>
  <div class="col-auto"><button class="btn btn-outline-secondary">Искать</button></div>
  <div class="col ms-auto text-end">
    <a class="btn btn-primary" href="{% url 'warehouse:product_create' %}">+ Товар</a>
    <a class="btn btn-outline-primary" href="{% url 'warehouse:stockin_create' %}">Приход</a>
    <a class="btn btn-outline-danger" href="{% url 'warehouse:stockmove_create' %}">Списание</a>
    <a class="btn btn-outline-secondary" href="{% url 'warehouse:inventory_create' %}">Инвентаризация</a>
  </div>
</form>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>Товар</th><th>Ед.</th><th class="text-end">Остаток</th><th class="text-end">Цена</th><th class="text-end">Стоимость остатка</th></tr></thead>
  <tbody>
  {% for p in object_list %}
    <tr>
      <td>{{ p.name }}</td><td>{{ p.unit }}</td>
      <td class="text-end">{{ p.stock_qty }}</td>
      <td class="text-end">{{ p.last_price }}</td>
      <td class="text-end">{{ p.stock_value }}</td>
    </tr>
  {% empty %}
    <tr><td colspan="5" class="text-muted">Нет данных</td></tr>
  {% endfor %}
  </tbody>
  <tfoot><tr><th colspan="4">Итого</th><th class="text-end">{{ stock_value }}</th></tr></tfoot>
</table>
{% endblock %}

```


---
## templates\warehouse\supplier_list.html
```html
{% extends 'base.html' %}{% block title %}Поставщики{% endblock %}{% block content %}
<h1 class="h4 mb-3">Поставщики</h1>
<div class="mb-3"><a class="btn btn-primary" href="{% url 'warehouse:supplier_create' %}">+ Поставщик</a></div>
<table class="table table-sm bg-white align-middle">
  <thead><tr><th>Название</th><th>Телефон</th><th>Примечание</th></tr></thead>
  <tbody>
    {% for s in object_list %}<tr><td>{{ s.name }}</td><td>{{ s.phone }}</td><td>{{ s.note }}</td></tr>{% empty %}
    <tr><td colspan="3" class="text-muted">Нет данных</td></tr>{% endfor %}
  </tbody>
</table>{% endblock %}

```


---
## templates\warehouse\techcard_detail.html
```html
{% extends 'base.html' %}
{% block title %}ТТК: {{ object.title }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h5 m-0">ТТК: {{ object.title }}</h1>
  <a class="btn btn-outline-primary btn-sm" href="{% url 'warehouse:techcardingredient_create' object.pk %}">+ Ингредиент</a>
</div>
<div class="card p-3 shadow-sm">
  <div class="small text-muted mb-2">Выход: {{ object.output_grams }} г</div>
  <table class="table table-sm align-middle">
    <thead><tr><th>Товар</th><th class="text-end">Кол-во</th><th class="text-end">Потери, %</th></tr></thead>
    <tbody>
      {% for ing in object.ingredients.all %}
        <tr>
          <td>{{ ing.product.name }}</td>
          <td class="text-end">{{ ing.qty }}</td>
          <td class="text-end">{{ ing.loss_percent }}</td>
        </tr>
      {% empty %}
        <tr><td colspan="3" class="text-muted">Ингредиентов нет</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}

```


---
## templates\_partials\pagination.html
```html
{% if page_obj and page_obj.has_other_pages %}
<nav>
  <ul class="pagination pagination-sm">
    {% if page_obj.has_previous %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">«</a></li>
    {% else %}
      <li class="page-item disabled"><span class="page-link">«</span></li>
    {% endif %}

    {% for i in page_obj.paginator.page_range %}
      {% if page_obj.number == i %}
        <li class="page-item active"><span class="page-link">{{ i }}</span></li>
      {% else %}
        <li class="page-item"><a class="page-link" href="?page={{ i }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">{{ i }}</a></li>
      {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
      <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}">»</a></li>
    {% else %}
      <li class="page-item disabled"><span class="page-link">»</span></li>
    {% endif %}
  </ul>
</nav>
{% endif %}

```


---
## warehouse\admin.py
```py
from django.contrib import admin

# Register your models here.

```


---
## warehouse\apps.py
```py
from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'

```


---
## warehouse\forms.py
```py
from django import forms
from .models import Product, Supplier, StockIn, StockMove, InventoryAdjustment, TechCard, TechCardIngredient


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'last_price', 'is_active']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'note']


class StockInForm(forms.ModelForm):

    class Meta:
        model = StockIn
        fields = ['date', 'product', 'supplier', 'qty', 'price_per_unit', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class StockMoveForm(forms.ModelForm):

    class Meta:
        model = StockMove
        fields = ['date', 'product', 'qty', 'reason']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class InventoryAdjustmentForm(forms.ModelForm):

    class Meta:
        model = InventoryAdjustment
        fields = ['date', 'product', 'delta', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class TechCardForm(forms.ModelForm):

    class Meta:
        model = TechCard
        fields = ['title', 'output_grams']


class TechCardIngredientForm(forms.ModelForm):

    class Meta:
        model = TechCardIngredient
        fields = ['product', 'qty', 'loss_percent']

```


---
## warehouse\models.py
```py
from decimal import Decimal
from django.db import models

UNIT_CHOICES = [('шт','шт'),('кг','кг'),('г','г'),('л','л'),('мл','мл')]


class Supplier(models.Model):
    name = models.CharField('Поставщик', max_length=200, unique=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    note = models.CharField('Примечание', max_length=200, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Товар', max_length=200, unique=True)
    unit = models.CharField('Ед. изм.', max_length=5, choices=UNIT_CHOICES, default='шт')
    last_price = models.DecimalField('Последняя цена за ед.', max_digits=12, decimal_places=2, default=0)
    stock_qty  = models.DecimalField('Остаток', max_digits=12, decimal_places=3, default=0)
    is_active  = models.BooleanField('Активен', default=True)

    def __str__(self):
        return self.name

    @property
    def stock_value(self):
        return (self.stock_qty or 0) * (self.last_price or 0)


class StockIn(models.Model):  # приход
    date = models.DateField('Дата')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ins')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.DecimalField('Кол-во', max_digits=12, decimal_places=3)
    price_per_unit = models.DecimalField('Цена за ед.', max_digits=12, decimal_places=2)
    note = models.CharField('Примечание', max_length=200, blank=True)

    def save(self, *a, **kw):
        super().save(*a, **kw)
        # апдейт цены и остатка
        p = self.product
        p.last_price = self.price_per_unit
        p.stock_qty = (p.stock_qty or Decimal('0')) + Decimal(self.qty)
        p.save(update_fields=['last_price','stock_qty'])


class StockMove(models.Model):  # списание
    date = models.DateField('Дата')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='moves')
    qty = models.DecimalField('Кол-во (минус)', max_digits=12, decimal_places=3)
    reason = models.CharField('Причина', max_length=200, blank=True)

    def save(self, *a, **kw):
        super().save(*a, **kw)
        p = self.product
        p.stock_qty = (p.stock_qty or Decimal('0')) - Decimal(self.qty)
        if p.stock_qty < 0: p.stock_qty = Decimal('0')
        p.save(update_fields=['stock_qty'])


class InventoryAdjustment(models.Model):  # инвентаризация
    date = models.DateField('Дата')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='adjustments')
    delta = models.DecimalField('Корректировка (+/-)', max_digits=12, decimal_places=3)
    note = models.CharField('Примечание', max_length=200, blank=True)

    def save(self, *a, **kw):
        super().save(*a, **kw)
        p = self.product
        p.stock_qty = (p.stock_qty or Decimal('0')) + Decimal(self.delta)
        if p.stock_qty < 0: p.stock_qty = Decimal('0')
        p.save(update_fields=['stock_qty'])


class TechCard(models.Model):  # ТТК (рецепт)
    title = models.CharField('Название блюда', max_length=200, unique=True)
    output_grams = models.PositiveIntegerField('Выход, г', default=0)
    def __str__(self): return self.title


class TechCardIngredient(models.Model):
    techcard = models.ForeignKey(TechCard, on_delete=models.CASCADE, related_name='ingredients')
    product  = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.DecimalField('Кол-во на блюдо', max_digits=12, decimal_places=3)
    loss_percent = models.PositiveIntegerField('Потери, %', default=0)

```


---
## warehouse\services.py
```py
from decimal import Decimal


def apply_stock_in(product, qty, price):
    product.last_price = price
    product.stock_qty = (product.stock_qty or 0) + Decimal(qty)
    product.save(update_fields=['last_price', 'stock_qty'])


def apply_stock_move(product, qty):
    product.stock_qty = (product.stock_qty or 0) - Decimal(qty)
    if product.stock_qty < 0:
        product.stock_qty = 0
    product.save(update_fields=['stock_qty'])


def apply_inventory_adjustment(product, delta):
    product.stock_qty = (product.stock_qty or 0) + Decimal(delta)
    if product.stock_qty < 0:
        product.stock_qty = 0
    product.save(update_fields=['stock_qty'])

```


---
## warehouse\tests.py
```py
from django.test import TestCase

# Create your tests here.

```


---
## warehouse\urls.py
```py
from django.urls import path
from . import views

app_name = 'warehouse'
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('new/', views.ProductCreateView.as_view(), name='product_create'),

    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', views.SupplierCreateView.as_view(), name='supplier_create'),

    path('in/new/', views.StockInCreateView.as_view(), name='stockin_create'),
    path('move/new/', views.StockMoveCreateView.as_view(), name='stockmove_create'),
    path('inventory/new/', views.InventoryAdjustmentCreateView.as_view(), name='inventory_create'),

    path('techcards/', views.TechCardListView.as_view(), name='techcard_list'),
    path('techcards/new/', views.TechCardCreateView.as_view(), name='techcard_create'),
    path('techcards/<int:pk>/', views.TechCardDetailView.as_view(), name='techcard_detail'),
    path('techcards/<int:pk>/add-ingredient/', views.TechCardIngredientCreateView.as_view(), name='techcardingredient_create'),
]

```


---
## warehouse\views.py
```py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import Product, Supplier, StockIn, StockMove, InventoryAdjustment, TechCard, TechCardIngredient
from .forms import *


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'warehouse/product_list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Product.objects.all().order_by('name')
        q = self.request.GET.get('q')
        if q: qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx['stock_value'] = sum(p.stock_value for p in ctx['object_list'])
        return ctx


class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = Product; form_class = ProductForm
    template_name = 'warehouse/product_form.html'
    success_url = '/warehouse/'


class SupplierListView(LoginRequiredMixin, generic.ListView):
    model = Supplier
    template_name = 'warehouse/supplier_list.html'


class SupplierCreateView(LoginRequiredMixin, generic.CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'warehouse/supplier_form.html'
    success_url = '/warehouse/suppliers/'

class StockInCreateView(LoginRequiredMixin, generic.CreateView):
    model = StockIn
    form_class = StockInForm
    template_name = 'warehouse/stockin_form.html'
    success_url = '/warehouse/'


class StockMoveCreateView(LoginRequiredMixin, generic.CreateView):
    model = StockMove; form_class = StockMoveForm
    template_name = 'warehouse/stockmove_form.html'; success_url = '/warehouse/'


class InventoryAdjustmentCreateView(LoginRequiredMixin, generic.CreateView):
    model = InventoryAdjustment; form_class = InventoryAdjustmentForm
    template_name = 'warehouse/inventory_form.html'; success_url = '/warehouse/'


class TechCardListView(LoginRequiredMixin, generic.ListView):
    model = TechCard; template_name = 'warehouse/techcard_list.html'


class TechCardCreateView(LoginRequiredMixin, generic.CreateView):
    model = TechCard; form_class = TechCardForm
    template_name = 'warehouse/techcard_form.html'; success_url = '/warehouse/techcards/'


class TechCardDetailView(LoginRequiredMixin, generic.DetailView):
    model = TechCard; template_name = 'warehouse/techcard_detail.html'


class TechCardIngredientCreateView(LoginRequiredMixin, generic.CreateView):
    model = TechCardIngredient; form_class = TechCardIngredientForm
    template_name = 'warehouse/techcardingredient_form.html'

    def form_valid(self, form):
        form.instance.techcard_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self): return f"/warehouse/techcards/{self.kwargs['pk']}/"

# быстрый плейсхолдер (если кто-то зашел на /warehouse/ напрямую):

def index(request):
    return HttpResponse("Откройте «Склад» → «Номенклатура».")

```


---
## warehouse\__init__.py
```py

```
