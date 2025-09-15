from django.urls import path
from .views import EventTaskCreateView, TaskListView

app_name = 'taskapp'
urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('event/<int:event_id>/new/', EventTaskCreateView.as_view(), name='event_task_create'),
]
