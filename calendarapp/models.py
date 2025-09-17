from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Hall(models.Model):
    name = models.CharField('Название зала', max_length=200)
    capacity = models.PositiveIntegerField('Вместимость', default=0)

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

    def __str__(self):
        return self.name


class Event(models.Model):
    class Slot(models.TextChoices):
        AM = 'am', _('День')
        PM = 'pm', _('Вечер')

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('в работе')
        CONFIRMED   = 'confirmed',   _('подтверждено')
        CANCELED    = 'canceled',    _('отменена')
        CLOSED      = 'closed',      _('закрыта')

    client  = models.ForeignKey('crm.Client', on_delete=models.PROTECT, related_name='events', verbose_name='Клиент')
    hall    = models.ForeignKey('calendarapp.Hall', on_delete=models.PROTECT, verbose_name='Зал')
    date    = models.DateField('Дата')
    slot    = models.CharField('Время', max_length=2, choices=Slot.choices)

    title   = models.CharField('Название/повод', max_length=200, blank=True)
    status  = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)

    guests  = models.PositiveIntegerField('Количество гостей', default=0)

    contract= models.FileField('Договор', upload_to='contracts/', blank=True)
    prepayment_amount = models.DecimalField('Предоплата, ₽', max_digits=12, decimal_places=2, default=0)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ответственный')

    # Метки времени по статусам
    confirmed_at = models.DateTimeField('Подтверждено в', null=True, blank=True)
    canceled_at  = models.DateTimeField('Отменено в', null=True, blank=True)
    closed_at    = models.DateTimeField('Закрыто в', null=True, blank=True)

    # Связь с блюдами (через промежуточную модель)
    dishes = models.ManyToManyField('menu.Dish', through='EventDish', related_name='events', blank=True, verbose_name='Блюда')

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        constraints = [
            models.UniqueConstraint(fields=['hall','date','slot'], name='unique_hall_date_slot')
        ]

    def __str__(self):
        return f"{self.date} • {self.get_slot_display()} • {self.hall}"

    def set_status(self, new_status):
        self.status = new_status
        now = timezone.now()
        if new_status == self.Status.CONFIRMED:
            self.confirmed_at = now
        elif new_status == self.Status.CANCELED:
            self.canceled_at = now
        elif new_status == self.Status.CLOSED:
            self.closed_at = now


class EventDish(models.Model):
    event = models.ForeignKey('calendarapp.Event', on_delete=models.CASCADE, related_name='dish_lines', verbose_name='Мероприятие')
    dish  = models.ForeignKey('menu.Dish', on_delete=models.PROTECT, related_name='event_lines', verbose_name='Блюдо')
    portions = models.PositiveIntegerField('Кол-во порций', default=1)
    price_at_time = models.DecimalField('Цена на момент добавления', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Блюдо в мероприятии'
        verbose_name_plural = 'Блюда в мероприятии'
        unique_together = (('event', 'dish'),)
