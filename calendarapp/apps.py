
from django.apps import AppConfig


class CalendarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarapp'
    verbose_name = 'Календарь/Мероприятия'

    def ready(self):
        # Подключим сигналы
        try:
            from . import signals  # noqa
        except Exception:
            # В патче модуль может отсутствовать до копирования
            pass
