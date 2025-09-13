from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponse
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import Product, Supplier, StockIn, StockMove, InventoryAdjustment, TechCard, TechCardIngredient
from .forms import *


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'warehouse/product_list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Product.objects.all().order_by('name')
        q = self.request.GET.get('q')
        if q: qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx['stock_value'] = sum(p.stock_value for p in ctx['object_list'])
        return ctx


class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = Product; form_class = ProductForm
    template_name = 'warehouse/product_form.html'
    success_url = '/warehouse/'


class SupplierListView(LoginRequiredMixin, generic.ListView):
    model = Supplier
    template_name = 'warehouse/supplier_list.html'


class SupplierCreateView(LoginRequiredMixin, generic.CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'warehouse/supplier_form.html'
    success_url = '/warehouse/suppliers/'

class StockInCreateView(LoginRequiredMixin, generic.CreateView):
    model = StockIn
    form_class = StockInForm
    template_name = 'warehouse/stockin_form.html'
    success_url = '/warehouse/'


class StockMoveCreateView(LoginRequiredMixin, generic.CreateView):
    model = StockMove; form_class = StockMoveForm
    template_name = 'warehouse/stockmove_form.html'; success_url = '/warehouse/'


class InventoryAdjustmentCreateView(LoginRequiredMixin, generic.CreateView):
    model = InventoryAdjustment; form_class = InventoryAdjustmentForm
    template_name = 'warehouse/inventory_form.html'; success_url = '/warehouse/'


class TechCardListView(LoginRequiredMixin, generic.ListView):
    model = TechCard; template_name = 'warehouse/techcard_list.html'


class TechCardCreateView(LoginRequiredMixin, generic.CreateView):
    model = TechCard; form_class = TechCardForm
    template_name = 'warehouse/techcard_form.html'; success_url = '/warehouse/techcards/'


class TechCardDetailView(LoginRequiredMixin, generic.DetailView):
    model = TechCard; template_name = 'warehouse/techcard_detail.html'


class TechCardIngredientCreateView(LoginRequiredMixin, generic.CreateView):
    model = TechCardIngredient; form_class = TechCardIngredientForm
    template_name = 'warehouse/techcardingredient_form.html'

    def form_valid(self, form):
        form.instance.techcard_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self): return f"/warehouse/techcards/{self.kwargs['pk']}/"

# быстрый плейсхолдер (если кто-то зашел на /warehouse/ напрямую):

def index(request):
    return HttpResponse("Откройте «Склад» → «Номенклатура».")
