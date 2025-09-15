from django.db import models

SOURCE_CHOICES = (
    ('yandex', 'Яндекс'),
    ('2gis', '2ГИС'),
    ('site', 'Сайт'),
    ('ref', 'Рекомендация'),
)
class Client(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=50)
    description = models.TextField('Описание', blank=True)
    source = models.CharField('Источник', max_length=32, choices=SOURCE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
