from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Группы блюд
    path('groups/', views.DishGroupListView.as_view(), name='group_list'),
    path('groups/add/', views.DishGroupCreateView.as_view(), name='group_add'),
    path('groups/<int:pk>/edit/', views.DishGroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.DishGroupDeleteView.as_view(), name='group_delete'),

    # Блюда внутри выбранной группы
    path('groups/<int:group_id>/dishes/', views.DishListInGroupView.as_view(), name='dish_list_in_group'),
    path('groups/<int:group_id>/dishes/add/', views.dish_create, name='dish_add_in_group'),

    # Отдельные операции по блюду
    path('dishes/<int:pk>/', views.DishDetailView.as_view(), name='dish_detail'),
    path('dishes/<int:pk>/edit/', views.dish_update, name='dish_edit'),
    path('dishes/<int:pk>/delete/', views.DishDeleteView.as_view(), name='dish_delete'),
]
