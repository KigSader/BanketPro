from django.db import models
from django.utils.translation import gettext_lazy as _


class DishGroup(models.Model):
    name = models.CharField(_('Группа блюд'), max_length=120, unique=True)
    description = models.TextField(_('Описание'), blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('Группа блюд')
        verbose_name_plural = _('Группы блюд')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Dish(models.Model):
    """
    Технологическая карта блюда:
    - Наименование (name)
    - Фото (photo)
    - Состав (composition_text) — для отображения в карточке
    - Стоимость (price)
    + Структурированный состав для склада — через RecipeItem
    """
    group = models.ForeignKey(DishGroup, on_delete=models.CASCADE, related_name='dishes', verbose_name=_('Группа'))
    name = models.CharField(_('Наименование'), max_length=160)
    photo = models.ImageField(_('Фото'), upload_to='dishes/', blank=True, null=True)
    composition_text = models.TextField(_('Состав'), blank=True)
    price = models.DecimalField(_('Стоимость'), max_digits=12, decimal_places=2)
    is_active = models.BooleanField(_('Активно'), default=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Блюдо')
        verbose_name_plural = _('Блюда')
        ordering = ('group__name', 'name')
        unique_together = (('group', 'name'),)

    def __str__(self):
        return f'{self.group.name} / {self.name}'


class RecipeItem(models.Model):
    """
    Строка рецепта — сколько продукта нужно на 1 порцию блюда.
    """
    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE, related_name='recipe_items', verbose_name=_('Блюдо'))
    product = models.ForeignKey('warehouse.Product', on_delete=models.PROTECT, related_name='recipe_items', verbose_name=_('Продукт'))
    quantity_per_portion = models.DecimalField(_('Кол-во на порцию'), max_digits=12, decimal_places=3)

    class Meta:
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецепте')
        unique_together = (('dish', 'product'),)

    def __str__(self):
        return f'{self.dish} -> {self.product} x {self.quantity_per_portion}'
