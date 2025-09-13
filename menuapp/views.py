from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import DishGroup, Dish, ClientMenu

class DishListView(LoginRequiredMixin, generic.ListView):
    model = Dish
    template_name = 'menu/dish_list.html'

class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    fields = ['name','photo','composition','serving_weight','group']
    template_name = 'menu/dish_form.html'
    success_url = '/menu/'

class DishGroupCreateView(LoginRequiredMixin, generic.CreateView):
    model = DishGroup
    fields = ['name']
    template_name = 'menu/dishgroup_form.html'
    success_url = '/menu/'

class ClientMenuCreateView(LoginRequiredMixin, generic.CreateView):
    model = ClientMenu
    fields = ['client','title','dishes']
    template_name = 'menu/clientmenu_form.html'
    success_url = '/menu/'
