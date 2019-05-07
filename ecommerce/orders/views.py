from django.shortcuts import render, Http404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template

from .models import Order, ProductPurchase
from billing.models import BillingProfile
from ecommerce.utils import render_to_pdf

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Order.objects.by_billing_profile(request = self.request).not_created()

class OrderDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        qs = Order.objects.by_billing_profile(request = self.request).filter(order_id = self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404('Order does not exist')

class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'
    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(request = self.request) # by_billing_profile(request = self.request).digital()

class VerifyOwnership(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            product_id = request.GET.get('product_id', None)
            if product_id:
                product_id = int(product_id)
                product_ids = ProductPurchase.objects.products_by_id(request)
                if product_id in product_ids:
                    return JsonResponse({'owner': True})
            return JsonResponse({'owner': False})
        raise Http404('Something went wrong!')

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        template = get_template('orders/order_invoice.html')
        qs = Order.objects.by_billing_profile(request = self.request).filter(order_id = self.kwargs.get('order_id'))
        order_obj = qs.first()
        context = {
            'order': order_obj
        }
        html = template.render(context)
        pdf = render_to_pdf('orders/order_invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type = 'application/pdf')
            filename = f'Invoice-{order_obj.order_id}.pdf'
            content = 'inline;filename=%s' %(filename)
            download = request.GET.get('download')
            if download:
                content = 'attachment;filename=%s' %(filename)
            response['Content-disposition'] = content
            return response
        return HttpResponse('Order invoice not found')