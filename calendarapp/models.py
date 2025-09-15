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