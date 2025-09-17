
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import ServiceCategory, Service
from .forms import ServiceCategoryForm, ServiceForm


class ServiceCategoryList(ListView):
    model = ServiceCategory
    template_name = 'serviceapp/category_list.html'
    context_object_name = 'categories'


class ServiceCategoryCreate(CreateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'serviceapp/category_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Категория создана.')
        return reverse('services:category_list')


class ServiceCategoryUpdate(UpdateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'serviceapp/category_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Категория обновлена.')
        return reverse('services:category_list')


class ServiceCategoryDelete(DeleteView):
    model = ServiceCategory
    template_name = 'serviceapp/category_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Категория удалена.')
        return reverse('services:category_list')


class ServiceList(ListView):
    model = Service
    template_name = 'serviceapp/service_list.html'
    context_object_name = 'services'


class ServiceCreate(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'serviceapp/service_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Услуга создана.')
        return reverse('services:service_list')


class ServiceUpdate(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'serviceapp/service_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Услуга обновлена.')
        return reverse('services:service_list')


class ServiceDelete(DeleteView):
    model = Service
    template_name = 'serviceapp/service_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Услуга удалена.')
        return reverse('services:service_list')
