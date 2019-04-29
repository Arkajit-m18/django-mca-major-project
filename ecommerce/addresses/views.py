from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import AddressForm, AddressEditForm
from .models import Address
from billing.models import BillingProfile

# Create your views here.

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'addresses/address_edit.html'
    model = Address
    form_class = AddressEditForm

    def get_object(self):
        billing_profile, created = BillingProfile.objects.new_or_get(self.request)
        return Address.objects.get(billing_profile = billing_profile)

    def get_success_url(self):
        return reverse('accounts:accounts_home')

class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'addresses/address_edit.html'
    model = Address
    form_class = AddressEditForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        billing_profile, created = BillingProfile.objects.new_or_get(self.request)
        self.object.billing_profile = billing_profile
        self.object.save()
        return super(AddressCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('accounts:accounts_home')

def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit = False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + '_address_id'] = instance.id
        else:
            print('Error')
            return redirect('carts:checkout')
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('carts:checkout')
    return redirect('carts:checkout')

def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == 'POST':
            address_type = request.POST.get('address_type', 'shipping')
            shipping_address = request.POST.get('shipping_address', None)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if shipping_address:
                qs = Address.objects.filter(billing_profile = billing_profile, id = shipping_address)
                if qs.exists():
                    request.session[address_type + '_address_id'] = shipping_address
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    return redirect('carts:checkout')
        