from django.urls import path
from . import views

app_name = 'crm'
urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/new/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),

    path('clients/search', views.clients_search, name='client_search'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
]
