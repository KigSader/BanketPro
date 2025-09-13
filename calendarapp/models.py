from django.db import models
from crm.models import Client

class Hall(models.Model):
    name = models.CharField('Зал', max_length=100)
    def __str__(self): return self.name

SLOT_CHOICES = [('am','Первая половина дня'),('pm','Вторая половина дня')]


class Event(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='events', verbose_name='Клиент')
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='events', verbose_name='Зал')
    date = models.DateField('Дата')
    slot = models.CharField('Слот', max_length=2, choices=SLOT_CHOICES)

    guests = models.PositiveIntegerField('Количество гостей', default=0)
    client_menu = models.ForeignKey('menuapp.ClientMenu', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Меню')
    contract = models.FileField('Договор', upload_to='contracts/', blank=True, null=True)

    prepayment_amount = models.DecimalField('Предоплата', max_digits=10, decimal_places=2, default=0)
    STATUS_CHOICES = [('draft','Черновик'),
                      ('pending','В работе'),
                      ('confirmed','Подтверждено'),
                      ('paid','Оплачено'),
                      ('canceled','Отменено')]

    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['hall','date','slot'], name='unique_hall_date_slot')]

    def __str__(self): return f"{self.date} {self.get_slot_display()} — {self.client}"
