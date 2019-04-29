from django.shortcuts import render

from django.views.generic import (
    ListView,
)

from products.models import Product

# Create your views here.
class SearchProductView(ListView):
    model = Product
    template_name = 'search/view.html'

    
    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        context['query_param'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        queryset = Product.objects
        request = self.request
        query_param = request.GET.get('q')
        if query_param is not None:
            return queryset.search(query_param)
        return Product.objects.featured()