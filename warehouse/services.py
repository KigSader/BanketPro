from decimal import Decimal


def apply_stock_in(product, qty, price):
    product.last_price = price
    product.stock_qty = (product.stock_qty or 0) + Decimal(qty)
    product.save(update_fields=['last_price', 'stock_qty'])


def apply_stock_move(product, qty):
    product.stock_qty = (product.stock_qty or 0) - Decimal(qty)
    if product.stock_qty < 0:
        product.stock_qty = 0
    product.save(update_fields=['stock_qty'])


def apply_inventory_adjustment(product, delta):
    product.stock_qty = (product.stock_qty or 0) + Decimal(delta)
    if product.stock_qty < 0:
        product.stock_qty = 0
    product.save(update_fields=['stock_qty'])
