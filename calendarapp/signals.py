# calendarapp/signals.py
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Event

# ===== 1) Запоминаем старый статус ДО сохранения =====
@receiver(pre_save, sender=Event)
def remember_old_status(sender, instance: Event, **kwargs):
    """
    Сохраняем прошлый статус до сохранения, чтобы в post_save понять факт смены.
    """
    if instance.pk:
        try:
            old = Event.objects.only('status').get(pk=instance.pk)
            instance._old_status = old.status
        except Event.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# ===== 2) После сохранения: автосоздание меню при confirmed =====
@receiver(post_save, sender=Event)
def auto_menu_on_confirmed(sender, instance: Event, created, **kwargs):
    """
    Если статус сменился на 'confirmed' и меню не привязано — создать пустое клиентское меню.
    """
    old_status = getattr(instance, '_old_status', None)
    if instance.status == 'confirmed' and old_status != 'confirmed' and not instance.client_menu:
        from menuapp.models import ClientMenu
        title = f"Меню {instance.date:%d.%m.%Y}"
        cm = ClientMenu.objects.create(client=instance.client, title=title)
        # Привязываем без изменения других полей
        instance.client_menu = cm
        instance.save(update_fields=['client_menu'])


# ===== 3) После сохранения: списание по ТТК при paid =====
@receiver(post_save, sender=Event)
def writeoff_on_paid(sender, instance: Event, created, **kwargs):
    """
    Если статус сменился на 'paid' и есть клиентское меню — списываем продукты по ТТК:
    need = qty_на_блюдо × кол-во гостей × (1 + потери/100)
    """
    old_status = getattr(instance, '_old_status', None)
    if instance.status != 'paid' or old_status == 'paid':
        return
    if not instance.client_menu or not instance.guests:
        return

    guests = Decimal(instance.guests)
    dishes = instance.client_menu.dishes.select_related('techcard').all()

    for dish in dishes:
        tech = getattr(dish, 'techcard', None)
        if not tech:
            continue
        for ing in tech.ingredients.select_related('product').all():
            base = Decimal(ing.qty or 0)
            loss = Decimal(ing.loss_percent or 0) / Decimal(100)
            need = (base * guests) * (Decimal(1) + loss)

            product = getattr(ing, 'product', None)
            if product is None:
                continue
            if product.stock_qty is None:
                product.stock_qty = Decimal('0')
            product.stock_qty = product.stock_qty - need
            if product.stock_qty < 0:
                product.stock_qty = Decimal('0')
            product.save(update_fields=['stock_qty'])
