# calendarapp/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.db.models.fields.related import ManyToManyField

from .models import Event
from crm.models import Client, SOURCE_CHOICES

# Радио-кнопки для UI
SLOT_CHOICES = (
    ('day', 'День'),
    ('evening', 'Вечер'),
    ('full', 'Полный день'),
)

# Соответствие UI-кодов к кодам в модели
SLOT_MAP = {'day': 'am', 'evening': 'pm'}

class EventCreateForm(forms.ModelForm):
    # --- Клиент (виртуальные поля) ---
    existing_client_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    new_full_name = forms.CharField(
        label='ФИО', max_length=255,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'Иванов Иван Иванович',
            'data-autocomplete-url': reverse_lazy('calendarapp:client_suggest'),
        })
    )
    new_phone       = forms.CharField(label='Телефон', max_length=32, required=False)
    new_source      = forms.ChoiceField(label='Источник', choices=SOURCE_CHOICES, required=False)
    new_description = forms.CharField(label='Описание', required=False, widget=forms.Textarea(attrs={'rows': 2}))

    # --- Время (день/вечер/полный день) ---
    slot_choice = forms.ChoiceField(label='Время', choices=SLOT_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Event
        fields = [
            'hall',               # Зал (FK)
            'date',               # Дата мероприятия (DateField)
            'title',              # Название/повод
            'guests',             # Кол-во гостей
            'prepayment_amount',  # Предоплата
            'client_menu',        # Меню (FK)
            'extras',             # Доп. услуги (M2M)
            # 'contract' — прикрепляется уже на карточке мероприятия
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Позволим вьюхе передать request, чтобы проставить initial из GET
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            q = self.request.GET
            if q.get('date'):
                self.fields['date'].initial = q['date']
            if q.get('hall'):
                try:
                    self.fields['hall'].initial = int(q['hall'])
                except ValueError:
                    pass
            if q.get('slot') in ('am', 'pm', 'full'):
                rev = {'am': 'day', 'pm': 'evening', 'full': 'full'}
                self.fields['slot_choice'].initial = rev[q['slot']]

    # --- Валидация занятости слотов ---
    def clean(self):
        cleaned = super().clean()
        hall = cleaned.get('hall')
        date = cleaned.get('date')
        slot_choice = cleaned.get('slot_choice')

        if not hall or not date or not slot_choice:
            return cleaned

        qs = Event.objects.filter(hall=hall, date=date)
        errors = []

        if slot_choice in ('day', 'evening'):
            slot_code = SLOT_MAP[slot_choice]          # 'am' или 'pm'
            if qs.filter(slot=slot_code).exists():
                errors.append(f'Слот «{dict(SLOT_CHOICES)[slot_choice]}» уже занят в выбранном зале и дате.')
        elif slot_choice == 'full':
            busy = []
            if qs.filter(slot='am').exists():
                busy.append('День')
            if qs.filter(slot='pm').exists():
                busy.append('Вечер')
            if busy:
                errors.append(f'Нельзя забронировать «Полный день»: занято — {", ".join(busy)}.')

        if errors:
            raise ValidationError(errors)

        return cleaned

    def save(self, user, commit=True):
        """
        Сохраняем event(ы) и создаём/находим клиента.
        Возвращаем основной event (для редиректа на detail).
        """
        cleaned = self.cleaned_data

        # 1) Клиент: поиск по hidden-id, иначе создание нового
        client = None
        if cleaned.get('existing_client_id'):
            try:
                client = Client.objects.get(pk=cleaned['existing_client_id'])
            except Client.DoesNotExist:
                client = None

        if client is None:
            client = Client.objects.create(
                full_name  = cleaned['new_full_name'],
                phone      = cleaned.get('new_phone') or '',
                source     = cleaned.get('new_source') or '',
                description= cleaned.get('new_description') or '',
            )

        # 2) Общие данные мероприятия
        base_kwargs = dict(
            client            = client,
            hall              = cleaned['hall'],
            date              = cleaned['date'],
            title             = cleaned.get('title') or '',
            guests            = cleaned.get('guests') or 0,
            prepayment_amount = cleaned.get('prepayment_amount') or 0,
            responsible       = user,      # кто создал — ответственный
            # status — оставим дефолт 'draft' из модели
        )

        slot_choice = cleaned['slot_choice']

        def _assign_field(e, field_name):
            """Аккуратно проставляем FK или M2M, если поле есть и не пустое."""
            if field_name not in self.cleaned_data:
                return
            value = self.cleaned_data[field_name]
            if value in (None, '', []):
                return
            try:
                field = e._meta.get_field(field_name)
            except Exception:
                return
            if isinstance(field, ManyToManyField):
                if not e.pk:
                    e.save()
                rel = getattr(e, field_name, None)
                if hasattr(rel, 'set'):
                    rel.set(value)
            else:
                setattr(e, field_name, value)
                if e.pk:
                    e.save(update_fields=[field_name])
                else:
                    e.save()

        def _create_event(slot_code: str):
            e = Event(**base_kwargs)
            e.slot = slot_code  # 'am' / 'pm'
            if commit:
                e.save()
                _assign_field(e, 'client_menu')
                _assign_field(e, 'extras')
            return e

        if slot_choice == 'full':
            first = _create_event('am')
            _create_event('pm')
            return first
        else:
            return _create_event(SLOT_MAP[slot_choice])
