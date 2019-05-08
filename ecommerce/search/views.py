from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import (
    ListView,
)

from products.models import Product

# Create your views here.
class SearchProductView(ListView):
    model = Product
    template_name = 'search/view.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.objects
        request = self.request
        query_param = request.GET.get('q')
        if query_param is not None:
            return queryset.search(query_param)
        return Product.objects.featured()
    
    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        query_param = self.request.GET.get('q')
        context['query_param'] = query_param
        search = Product.objects.search(query_param)
        paginator = Paginator(search, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context['product_list'] = products
        return context
