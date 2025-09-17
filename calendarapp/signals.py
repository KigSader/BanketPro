
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Event
from warehouse.services import writeoff_for_event, revert_writeoff_for_event


@receiver(pre_save, sender=Event)
def _remember_old_status(sender, instance: Event, **kwargs):
    if instance.pk:
        try:
            old = Event.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Event.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Event)
def _on_status_change(sender, instance: Event, created, **kwargs):
    old = getattr(instance, "_old_status", None)
    new = instance.status

    # Подтвердили: списываем ингредиенты (идемпотентно)
    if old != new and new == Event.Status.CONFIRMED:
        try:
            writeoff_for_event(instance)
        except Exception:
            # по желанию: логируйте ошибку
            pass

    # Отменили подтвержденное — вернем на склад
    if old != new and old == Event.Status.CONFIRMED and new == Event.Status.CANCELED:
        try:
            revert_writeoff_for_event(instance)
        except Exception:
            pass
