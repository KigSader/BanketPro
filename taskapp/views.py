from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import Task
from .forms import TaskForm
from calendarapp.models import Event

class EventTaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['event_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.event = self.event
        form.instance.client = self.event.client
        return super().form_valid(form)

    def get_success_url(self):
        return f"/calendar/{self.event.pk}/"

class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    paginate_by = 50
    def get_queryset(self):
        qs = super().get_queryset()
        s = self.request.GET.get('status')
        if s:
            qs = qs.filter(status=s)
        return qs.select_related('event','client','responsible')
