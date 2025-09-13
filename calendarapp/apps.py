from django.apps import AppConfig


class CalendarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarapp'
    verbose_name = 'Календарь и мероприятия'

    def ready(self):
        # импортируем signals, чтобы Django их «зарегистрировал»
        import calendarapp.signals  # noqa
