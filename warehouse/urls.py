from django.urls import path
from . import views

app_name = 'warehouse'
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('new/', views.ProductCreateView.as_view(), name='product_create'),

    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', views.SupplierCreateView.as_view(), name='supplier_create'),

    path('in/new/', views.StockInCreateView.as_view(), name='stockin_create'),
    path('move/new/', views.StockMoveCreateView.as_view(), name='stockmove_create'),
    path('inventory/new/', views.InventoryAdjustmentCreateView.as_view(), name='inventory_create'),

    path('techcards/', views.TechCardListView.as_view(), name='techcard_list'),
    path('techcards/new/', views.TechCardCreateView.as_view(), name='techcard_create'),
    path('techcards/<int:pk>/', views.TechCardDetailView.as_view(), name='techcard_detail'),
    path('techcards/<int:pk>/add-ingredient/', views.TechCardIngredientCreateView.as_view(), name='techcardingredient_create'),
]
