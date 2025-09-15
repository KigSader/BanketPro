from django.urls import path
from . import views
app_name='menuapp'
urlpatterns = [
  path('', views.DishListView.as_view(), name='dish_list'),
  path('new/', views.DishCreateView.as_view(), name='dish_create'),
  path('groups/new/', views.DishGroupCreateView.as_view(), name='dishgroup_create'),
  path('clientmenu/new/', views.ClientMenuCreateView.as_view(), name='clientmenu_create'),
  path('extras/', views.ExtraServiceListView.as_view(), name='extras_list'),
  path('extras/new/', views.ExtraServiceCreateView.as_view(), name='extras_create'),
]
