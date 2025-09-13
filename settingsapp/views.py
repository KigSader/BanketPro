from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import redirect
from calendarapp.models import Hall
from employees.models import PayrollSettings
from .forms import HallForm, PayrollSettingsForm

class SettingsHomeView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'settingsapp/home.html'

class HallListView(LoginRequiredMixin, generic.ListView):
    model = Hall; template_name = 'settingsapp/hall_list.html'

class HallCreateView(LoginRequiredMixin, generic.CreateView):
    model = Hall; form_class = HallForm
    template_name = 'settingsapp/hall_form.html'; success_url = '/settings/halls/'

class PayrollSettingsView(LoginRequiredMixin, generic.FormView):
    template_name = 'settingsapp/payroll_form.html'; form_class = PayrollSettingsForm
    success_url = '/settings/payroll/'
    def get_initial(self):
        ps, _ = PayrollSettings.objects.get_or_create(pk=1)
        return {'kitchen_percent': ps.kitchen_percent, 'service_percent': ps.service_percent}
    def form_valid(self, form):
        ps, _ = PayrollSettings.objects.get_or_create(pk=1)
        ps.kitchen_percent = form.cleaned_data['kitchen_percent']
        ps.service_percent = form.cleaned_data['service_percent']
        ps.save()
        return super().form_valid(form)
