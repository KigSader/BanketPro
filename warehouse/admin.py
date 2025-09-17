from django.contrib import admin
from .models import Product, StockMovement


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'current_qty', 'min_qty', 'is_active')
    search_fields = ('name', 'sku')
    list_filter = ('unit', 'is_active')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'qty_change', 'kind', 'event')
    list_filter = ('kind', 'created_at')
    search_fields = ('product__name', 'event__id')
