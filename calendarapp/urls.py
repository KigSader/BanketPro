from django.urls import path
from . import views

app_name = 'calendarapp'

urlpatterns = [
    path('add/', views.EventCreateView.as_view(), name='event_create'),
    path('clients/suggest/', views.client_suggest, name='client_suggest'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
]
