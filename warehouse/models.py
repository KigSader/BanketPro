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
