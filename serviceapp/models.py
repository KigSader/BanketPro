
from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceCategory(models.Model):
    name = models.CharField(_('Категория'), max_length=160, unique=True)

    class Meta:
        verbose_name = _('Категория услуги')
        verbose_name_plural = _('Категории услуг')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services', verbose_name=_('Категория'))
    name = models.CharField(_('Наименование'), max_length=160)
    description = models.TextField(_('Описание'), blank=True)
    photo = models.ImageField(_('Фото'), upload_to='services/', blank=True, null=True)
    price = models.DecimalField(_('Базовая стоимость'), max_digits=12, decimal_places=2)
    is_active = models.BooleanField(_('Активна'), default=True)

    class Meta:
        verbose_name = _('Услуга')
        verbose_name_plural = _('Услуги')
        unique_together = (('category', 'name'),)

    def __str__(self):
        return self.name


class EventServiceLine(models.Model):
    event = models.ForeignKey('calendarapp.Event', on_delete=models.CASCADE, related_name='service_lines', verbose_name=_('Мероприятие'))
    service = models.ForeignKey('serviceapp.Service', on_delete=models.PROTECT, related_name='event_lines', verbose_name=_('Услуга'))
    quantity = models.PositiveIntegerField(_('Кол-во'), default=1)
    unit_price = models.DecimalField(_('Цена за ед.'), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _('Услуга в мероприятии')
        verbose_name_plural = _('Услуги в мероприятии')
        unique_together = (('event', 'service'),)

    @property
    def total(self):
        return self.quantity * self.unit_price
