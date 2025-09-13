from django import forms
from .models import Product, Supplier, StockIn, StockMove, InventoryAdjustment, TechCard, TechCardIngredient


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'last_price', 'is_active']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'note']


class StockInForm(forms.ModelForm):

    class Meta:
        model = StockIn
        fields = ['date', 'product', 'supplier', 'qty', 'price_per_unit', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class StockMoveForm(forms.ModelForm):

    class Meta:
        model = StockMove
        fields = ['date', 'product', 'qty', 'reason']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class InventoryAdjustmentForm(forms.ModelForm):

    class Meta:
        model = InventoryAdjustment
        fields = ['date', 'product', 'delta', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class TechCardForm(forms.ModelForm):

    class Meta:
        model = TechCard
        fields = ['title', 'output_grams']


class TechCardIngredientForm(forms.ModelForm):

    class Meta:
        model = TechCardIngredient
        fields = ['product', 'qty', 'loss_percent']
