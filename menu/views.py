from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import DishGroup, Dish
from .forms import DishGroupForm, DishForm, RecipeItemFormSet


# -------- ГРУППЫ --------
class DishGroupListView(LoginRequiredMixin, ListView):
    model = DishGroup
    template_name = 'menuapp/group_list.html'
    context_object_name = 'groups'


class DishGroupCreateView(LoginRequiredMixin, CreateView):
    model = DishGroup
    form_class = DishGroupForm
    template_name = 'menuapp/group_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Группа создана. Теперь добавьте блюда внутри группы.')
        return reverse('menu:group_list')


class DishGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = DishGroup
    form_class = DishGroupForm
    template_name = 'menuapp/group_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Группа обновлена.')
        return reverse('menu:group_list')


class DishGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = DishGroup
    template_name = 'menuapp/group_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Группа удалена.')
        return reverse('menu:group_list')


# -------- БЛЮДА --------
class DishListInGroupView(LoginRequiredMixin, ListView):
    model = Dish
    template_name = 'menuapp/dish_list.html'
    context_object_name = 'dishes'

    def get_queryset(self):
        self.group = get_object_or_404(DishGroup, pk=self.kwargs['group_id'])
        return (
            Dish.objects.filter(group=self.group)
            .select_related('group')
            .prefetch_related('recipe_items__product')
            .order_by('name')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['group'] = self.group
        return ctx


@login_required
@transaction.atomic
def dish_create(request, group_id):
    group = get_object_or_404(DishGroup, pk=group_id)
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        formset = RecipeItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            dish = form.save(commit=False)
            dish.group = group  # фиксируем группу на сервере
            dish.save()
            formset.instance = dish
            formset.save()
            messages.success(request, 'Блюдо создано.')
            return redirect('menu:dish_list_in_group', group_id=group.id)
    else:
        form = DishForm(initial={'group': group.id})
        # сузим выбор группы до одной (для UX и защиты)
        if 'group' in form.fields:
            form.fields['group'].queryset = DishGroup.objects.filter(pk=group.id)
        formset = RecipeItemFormSet()
    return render(request, 'menuapp/dish_form.html', {'form': form, 'formset': formset, 'group': group})


@login_required
@transaction.atomic
def dish_update(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        formset = RecipeItemFormSet(request.POST, instance=dish)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Блюдо обновлено.')
            return redirect('menu:dish_list_in_group', group_id=dish.group_id)
    else:
        form = DishForm(instance=dish)
        # опционально: не позволяем перекидывать блюдо в другую группу
        if 'group' in form.fields:
            form.fields['group'].queryset = DishGroup.objects.filter(pk=dish.group_id)
        formset = RecipeItemFormSet(instance=dish)
    return render(
        request,
        'menuapp/dish_form.html',
        {'form': form, 'formset': formset, 'group': dish.group, 'dish': dish}
    )


class DishDeleteView(LoginRequiredMixin, DeleteView):
    model = Dish
    template_name = 'menuapp/dish_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Блюдо удалено.')
        return reverse('menu:dish_list_in_group', kwargs={'group_id': self.object.group_id})


class DishDetailView(LoginRequiredMixin, DetailView):
    model = Dish
    template_name = 'menuapp/dish_detail.html'
    context_object_name = 'dish'
