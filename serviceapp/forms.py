from django import forms
from .models import ServiceCategory, Service


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ('name',)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('category', 'name', 'description', 'photo', 'price', 'is_active')
