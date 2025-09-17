from django import forms
from django.forms import inlineformset_factory
from .models import DishGroup, Dish, RecipeItem


class DishGroupForm(forms.ModelForm):
    class Meta:
        model = DishGroup
        fields = ('name', 'description')


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ('group', 'name', 'photo', 'composition_text', 'price', 'is_active')

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price < 0:
            raise forms.ValidationError('Стоимость не может быть отрицательной.')
        return price


RecipeItemFormSet = inlineformset_factory(
    Dish,
    RecipeItem,
    fields=('product', 'quantity_per_portion'),
    extra=1,
    can_delete=True
)
