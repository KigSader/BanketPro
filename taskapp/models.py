from django.db import models
from django.conf import settings

class Task(models.Model):
    STATUS_CHOICES = [('in_progress','В работе'), ('done','Завершена'), ('canceled','Отменена')]
    TYPE_CHOICES = [('call','Звонок'), ('meeting','Встреча'), ('prepayment','Предоплата')]

    event = models.ForeignKey('calendarapp.Event', on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    client = models.ForeignKey('crm.Client', on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)

    task_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default='call')
    description = models.CharField('Описание', max_length=300)
    deadline = models.DateTimeField('Дедлайн', null=True, blank=True)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Ответственный',
                                    on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='in_progress')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['status','deadline','-id']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f"{self.get_task_type_display()}: {self.description[:30]}"
