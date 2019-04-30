from django.shortcuts import render, Http404, HttpResponse, redirect
from django.views.generic import (
    ListView,
    DetailView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from wsgiref.util import FileWrapper
from mimetypes import guess_type
from django.contrib import messages

from .models import Product, ProductFile
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
from orders.models import ProductPurchase
# from analytics.signals import object_viewed_signal

import os

# Create your views here.
class ProductListView(ListView):
    model = Product
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        all_products = Product.objects.all()
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context['product_list'] = products
        return context

class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = 'products/user_product_history.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(**kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        all_views = self.request.user.objectviewed_set.by_model(model_class = Product)
        paginator = Paginator(all_views, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            views = paginator.page(page)
        except PageNotAnInteger:
            views = paginator.page(1)
        except EmptyPage:
            views = paginator.page(paginator.num_pages)
        context['view_list'] = views
        return context
    
    def get_queryset(self, *args, **kwargs):
        views = self.request.user.objectviewed_set.by_model(model_class = Product)
        return views

class ProductDetailView(ObjectViewedMixin, DetailView):
    model = Product

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        request = self.request
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist!")
        return instance

class ProductSlugDetailView(ObjectViewedMixin, DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductSlugDetailView, self).get_context_data(**kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context
    

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        request = self.request
        instance = Product.objects.get_by_slug(slug)
        if instance is None:
            raise Http404("Product doesn't exist!")
        # object_viewed_signal.send(instance.__class__, instance = instance, request = request)
        return instance

class ProductFeaturedListView(ListView):
    template_name = 'products/product_featured_list.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()
        
        # queryset = super().get_queryset()
        # return queryset.filter(featured = True)

class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/product_featured_detail.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()

        # queryset = super().get_queryset()
        # return queryset.filter(featured = True)

class ProductSlugFeaturedDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/product_featured_detail.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()

class ProductDownloadView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        # qs = Product.objects.filter(slug = slug)
        # if qs.count() != 1:
        #     raise Http404("Product not found!")
        # product_obj = qs.first()
        # downloads_qs = product_obj.get_downloads().filter(pk = pk)
        # if downloads_qs.count() != 1:
        #     raise Http404("Download not found!")
        download_qs = ProductFile.objects.filter(pk = pk, product__slug = slug)
        if download_qs.count() != 1:
            raise Http404("Download not found!")
        download_obj = download_qs.first()

        can_download = False
        user_ready = True
        if download_obj.user_required:  
            if not request.user.is_authenticated:
                user_ready = False
            #     user_can_download = True
            # else:
            #     user_can_download = False

        purchased_products = Product.objects.none()
        if download_obj.free:
            can_download = True
        else:
            purchased_products = ProductPurchase.objects.products_by_request(request)
            if download_obj.product in purchased_products:
                can_download = True

        if not can_download or not user_ready:
            messages.error(request, "You do not have access to download this item")
            return redirect(download_obj.get_default_url())
        

        file_root = settings.PROTECTED_ROOT
        file_path = download_obj.product_file.path
        final_filepath = os.path.join(file_root, file_path)
        with open(final_filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mimetype = 'application/force-download'
            guessed_mimetype = guess_type(file_path)[0]
            if guessed_mimetype:
                mimetype = guessed_mimetype
            response = HttpResponse(wrapper, content_type = mimetype)
            response['Content-Disposition'] = 'attachment;filename=%s' %(download_obj.name)
            response['X-SendFile'] = str(download_obj.name)
            return response
