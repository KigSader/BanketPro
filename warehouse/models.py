from decimal import Decimal
from django.db import models, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    UNIT_CHOICES = [
        ('g', _('г')),
        ('kg', _('кг')),
        ('ml', _('мл')),
        ('l', _('л')),
        ('pcs', _('шт')),
    ]

    name = models.CharField(_('Продукт'), max_length=160, unique=True)
    sku = models.CharField(_('Артикул'), max_length=64, blank=True)
    unit = models.CharField(_('Ед. изм.'), max_length=8, choices=UNIT_CHOICES, default='g')
    current_qty = models.DecimalField(_('Остаток'), max_digits=14, decimal_places=3, default=Decimal('0'))
    cost_per_unit = models.DecimalField(_('Себестоимость за единицу'), max_digits=12, decimal_places=4, default=Decimal('0'))
    min_qty = models.DecimalField(_('Минимальный остаток'), max_digits=14, decimal_places=3, default=Decimal('0'))
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    @property
    def stock_value(self):
        return self.current_qty * self.cost_per_unit

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')
        ordering = ('name',)

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        PURCHASE = 'PURCHASE', _('Закупка')
        ADJUSTMENT = 'ADJUSTMENT', _('Корректировка')
        EVENT_WRITEOFF = 'EVENT_WRITEOFF', _('Списание по мероприятию')
        EVENT_RETURN = 'EVENT_RETURN', _('Возврат после отмены')

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements', verbose_name=_('Продукт'))
    qty_change = models.DecimalField(_('Изменение кол-ва'), max_digits=14, decimal_places=3)
    kind = models.CharField(_('Тип операции'), max_length=32, choices=Kind.choices)
    event = models.ForeignKey('calendarapp.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements', verbose_name=_('Мероприятие'))
    note = models.CharField(_('Комментарий'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('Движение склада')
        verbose_name_plural = _('Движения склада')
        indexes = [
            models.Index(fields=('event', 'kind')),
        ]

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d} {self.product} {self.qty_change} ({self.kind})'
