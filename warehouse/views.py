from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Product, StockMovement
from .forms import ProductForm, StockMovementForm

class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'warehouse/product_list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Product.objects.all().order_by('name')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        # опираемся на @property stock_value, который мы добавили в models.py
        ctx['stock_value'] = sum((p.stock_value or 0) for p in ctx['object_list'])
        return ctx

class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'warehouse/product_form.html'
    success_url = '/warehouse/'

class StockMovementCreateView(LoginRequiredMixin, generic.CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'warehouse/stockmovement_form.html'
    success_url = '/warehouse/'
