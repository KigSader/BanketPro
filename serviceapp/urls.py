
from django.urls import path
from serviceapp import views

app_name = 'services'

urlpatterns = [
    path('categories/', views.ServiceCategoryList.as_view(), name='category_list'),
    path('categories/add/', views.ServiceCategoryCreate.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.ServiceCategoryUpdate.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.ServiceCategoryDelete.as_view(), name='category_delete'),

    path('', views.ServiceList.as_view(), name='service_list'),
    path('add/', views.ServiceCreate.as_view(), name='service_add'),
    path('<int:pk>/edit/', views.ServiceUpdate.as_view(), name='service_edit'),
    path('<int:pk>/delete/', views.ServiceDelete.as_view(), name='service_delete'),
]
