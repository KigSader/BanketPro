from django.contrib import admin
from menu.models import DishGroup, Dish, RecipeItem


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 0


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'price', 'is_active')
    list_filter = ('group', 'is_active')
    search_fields = ('name', 'group__name')
    inlines = [RecipeItemInline]


@admin.register(DishGroup)
class DishGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
