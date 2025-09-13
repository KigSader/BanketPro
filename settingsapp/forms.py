from django import forms
from calendarapp.models import Hall
from employees.models import PayrollSettings

class HallForm(forms.ModelForm):
    class Meta: model = Hall; fields = ['name']

class PayrollSettingsForm(forms.ModelForm):
    class Meta: model = PayrollSettings; fields = ['kitchen_percent','service_percent']
