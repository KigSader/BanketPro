from django.db import models

class Expense(models.Model):
    TYPES = [('хоз','Хоз'),('аренда','Аренда'),('комм','Коммуналка'),('ремонт','Ремонт'),
             ('реклама','Реклама'),('обслуж','Обслуживание'),('др','Другое')]
    date = models.DateField('Дата')
    type = models.CharField('Тип', max_length=10, choices=TYPES)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    note = models.CharField('Комментарий', max_length=200, blank=True)

    class Meta: ordering = ['-date', '-id']
    def __str__(self): return f"{self.date} • {self.get_type_display()} • {self.amount}"
