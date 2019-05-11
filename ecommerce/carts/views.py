from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

from decimal import Decimal

from .models import Cart
from products.models import Product
from orders.models import Order
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address

import stripe
STRIPE_PUBLISH_KEY = getattr(settings, 'STRIPE_PUBLISH_KEY', "pk_test_poMIyXRk0ctfJGKxpJYeHa94")
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', "sk_test_nVVDnn3MEp769przNtUCPEuN")
stripe.api_key = STRIPE_SECRET_KEY

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{'id':product.id, 'name': product.title, 'price': product.price, 'url': product.get_absolute_url()} for product in cart_obj.products.all()]
    json_data = {
        'products': products,
        'subtotal': cart_obj.subtotal,
        'total': cart_obj.total,
    }
    return JsonResponse(json_data)

def cart_quantity_api_view(request):
    product_id = request.POST.get('product_id')
    product_qty = request.POST.get('product_qty')
    has_increased = request.POST.get('has_increased')
    has_decreased = request.POST.get('has_decreased')
    current_value = int(request.POST.get('current_value'))
    old_value = int(request.POST.get('old_value'))
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    product = cart_obj.products.get(id = product_id)
    new_price = Decimal(current_value) * product.price
    # if has_increased:
    cart_obj.total -= Decimal(old_value) * product.price
    cart_obj.total += Decimal(current_value) * product.price
    cart_obj.subtotal = cart_obj.total
    cart_obj.save()
    json_data = {
        'subtotal': cart_obj.subtotal,
        'total': cart_obj.total,
        'new_price': new_price,
        'original_price': product.price,
        'product_qty': product_qty,
    }
    return JsonResponse(json_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, 'carts/home.html', {'cart': cart_obj})

def cart_update(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return redirect('carts:cart_home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
            # cart_obj.products.add(product_id)
        request.session['cart_items'] = cart_obj.products.count()
        if request.is_ajax():
            print('Ajax request')
            json_data = {
                'added': added,
                'removed': not added,
                'cartItemCount': cart_obj.products.count(),
            }
            return JsonResponse(json_data)
            # return JsonResponse({'message': 'Error'}, status = 400)
    return redirect('carts:cart_home')

def checkout_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    if new_obj or cart_obj.products.count() == 0:
        return redirect('carts:cart_home')
    # else:
    #     order_obj, new_order_obj = Order.objects.get_or_create(cart = cart_obj)

    order_obj = None
    address_qs = None
    login_form = LoginForm(request = request)
    guest_form = GuestForm(request = request)
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get('shipping_address_id', None)
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    has_card = False

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile = billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile = billing_profile, cart_obj = cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id = shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id = billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

    if request.method == 'POST':
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, charge_msg = billing_profile.charge(order_obj = order_obj)
            if did_charge:
                order_obj.mark_paid()
                order_obj.send_confirmation(request)
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                return redirect('carts:success')
            else:
                print(charge_msg)
                return redirect('carts:checkout')

    context = {
        'order': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        'has_card': has_card,
        'publish_key': STRIPE_PUBLISH_KEY,
        'shipping_address_required': shipping_address_required,
    }
    return render(request, 'carts/checkout.html', context)

def checkout_done(request):
    return render(request, 'carts/checkout_done.html', {})