from django.urls import path
from .views import SettingsHomeView, HallListView, HallCreateView, PayrollSettingsView

app_name='settingsapp'
urlpatterns = [
    path('', SettingsHomeView.as_view(), name='home'),
    path('halls/', HallListView.as_view(), name='hall_list'),
    path('halls/new/', HallCreateView.as_view(), name='hall_create'),
    path('payroll/', PayrollSettingsView.as_view(), name='payroll'),
]
