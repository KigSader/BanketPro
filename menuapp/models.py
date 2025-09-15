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
