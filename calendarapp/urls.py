from django.urls import path
from . import views

app_name = 'calendarapp'
urlpatterns = [
    path('', views.EventListView.as_view(), name='calendar'),
    path('add/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
]
