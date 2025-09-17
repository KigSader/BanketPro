from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password_reset...

    path('crm/', include('crm.urls')),
    path('calendar/', include('calendarapp.urls')),
    path('menu/', include('menu.urls')),
    path('employees/', include('employees.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('expenses/', include('expenses.urls')),
    path('stats/', include('stats.urls')),
    path('settings/', include('settingsapp.urls')),
    path('tasks/', include('taskapp.urls')),


    # Админка существует, но ссылку в шапке мы НЕ показываем
    path('admin/', admin.site.urls),
]
