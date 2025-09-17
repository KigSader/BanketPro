from django.urls import path
from . import views

app_name = 'warehouse'
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('new/', views.ProductCreateView.as_view(), name='product_create'),
    path('movement/new/', views.StockMovementCreateView.as_view(), name='stockmovement_create'),
]
