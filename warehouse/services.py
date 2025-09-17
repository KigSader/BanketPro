from django.db.models import F
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, StockMovement


def required_products_for_event(event):
    """
    Возвращает словарь {product: total_qty}, который нужен на мероприятие
    исходя из блюд и кол-ва порций.
    """
    totals = defaultdict(Decimal)
    for line in event.dish_lines.select_related('dish').all():
        portions = Decimal(line.portions)
        # ингредиенты на 1 порцию
        for ri in line.dish.recipe_items.select_related('product').all():
            totals[ri.product] += (ri.quantity_per_portion * portions)
    return totals


@transaction.atomic
def writeoff_for_event(event):
    """
    Списание ингредиентов при подтверждении мероприятия.
    Идемпотентно: повторный вызов не создаст дубль.
    """
    from calendarapp.models import Event  # локальный импорт, чтобы избежать циклов
    if event.status != Event.Status.CONFIRMED:
        raise ValidationError('Списание возможно только для подтвержденного мероприятия.')

    # Уже списано?
    exists = StockMovement.objects.filter(event=event, kind=StockMovement.Kind.EVENT_WRITEOFF).exists()
    if exists:
        return False  # ничего не делаем

    totals = required_products_for_event(event)

    # Создаем движения и уменьшаем остатки
    for product, qty in totals.items():
        StockMovement.objects.create(
            product=product,
            qty_change=-qty,
            kind=StockMovement.Kind.EVENT_WRITEOFF,
            event=event,
            note=f'Списание по мероприятию #{event.pk}'
        )
        # обновим остаток атомарно
        Product.objects.filter(pk=product.pk).update(current_qty=F('current_qty') - qty)

    return True


@transaction.atomic
def revert_writeoff_for_event(event):
    """
    Возврат ингредиентов, если подтвержденное мероприятие отменили.
    Делает обратные движения, если было списание.
    """
    has_writeoff = StockMovement.objects.filter(event=event, kind=StockMovement.Kind.EVENT_WRITEOFF).exists()
    if not has_writeoff:
        return False

    totals = required_products_for_event(event)
    for product, qty in totals.items():
        StockMovement.objects.create(
            product=product,
            qty_change=qty,
            kind=StockMovement.Kind.EVENT_RETURN,
            event=event,
            note=f'Возврат после отмены #{event.pk}'
        )
        Product.objects.filter(pk=product.pk).update(current_qty=F('current_qty') + qty)

    return True
