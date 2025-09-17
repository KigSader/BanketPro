from django.contrib import admin
from .models import ServiceCategory, Service, EventServiceLine


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(EventServiceLine)
class EventServiceLineAdmin(admin.ModelAdmin):
    list_display = ('event', 'service', 'quantity', 'unit_price')
    search_fields = ('event__id', 'service__name')
