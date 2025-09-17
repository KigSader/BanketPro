
from django.core.management.base import BaseCommand
from django.utils import timezone
from calendarapp.models import Event


class Command(BaseCommand):
    help = 'Ежедневно закрывает прошедшие мероприятия (если не отменены).'

    def handle(self, *args, **options):
        today = timezone.localdate()
        qs = Event.objects.filter(
            status__in=[Event.Status.IN_PROGRESS, Event.Status.CONFIRMED],
            date__lt=today
        )
        updated = 0
        for ev in qs:
            ev.set_status(Event.Status.CLOSED)
            ev.save(update_fields=['status', 'closed_at'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Закрыто мероприятий: {updated}'))
