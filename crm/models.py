from django.db import models

class Client(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=50)
    description = models.TextField('Описание', blank=True)
    source = models.CharField('Источник', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.full_name
