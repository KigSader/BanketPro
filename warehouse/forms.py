from django import forms
from .models import Product, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'unit', 'current_qty', 'cost_per_unit', 'min_qty', 'is_active']

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'qty_change', 'kind', 'event', 'note']