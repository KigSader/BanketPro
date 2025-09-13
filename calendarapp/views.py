from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django import forms
from django.urls import reverse
from .models import Event

class EventForm(forms.ModelForm):
    slot_full = forms.BooleanField(label='Полный день', required=False)
    class Meta:
        model = Event
        fields = ['client','hall','date','slot','guests','client_menu','contract','prepayment_amount','status']
        widgets = {'date': forms.DateInput(attrs={'type':'date'})}
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if request:
            d = request.GET.get('date'); s = request.GET.get('slot')
            if d: self.fields['date'].initial = d
            if s in ('am','pm'): self.fields['slot'].initial = s
            if s == 'full': self.fields['slot_full'].initial = True

class EventListView(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'calendar/calendar_list.html'
    ordering = ['date']

class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = 'calendar/event_form.html'
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    def form_valid(self, form):
        full = form.cleaned_data.pop('slot_full', False)
        resp = super().form_valid(form)
        if full:
            other = 'pm' if self.object.slot == 'am' else 'am'
            Event.objects.create(
                client=self.object.client, hall=self.object.hall,
                date=self.object.date, slot=other,
                guests=self.object.guests, client_menu=self.object.client_menu,
                contract=self.object.contract, prepayment_amount=self.object.prepayment_amount,
                status=self.object.status,
            )
        return resp
    def get_success_url(self):
        return reverse('crm:dashboard')

class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    template_name = 'calendar/event_detail.html'
