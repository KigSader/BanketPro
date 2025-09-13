from django.urls import path
from .views import DashboardStatsView
app_name='stats'
urlpatterns = [ path('', DashboardStatsView.as_view(), name='dashboard') ]
