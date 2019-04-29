from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.utils.http import is_safe_url
from django.conf import settings

from .models import BillingProfile, Card

import stripe
STRIPE_PUBLISH_KEY = getattr(settings, 'STRIPE_PUBLISH_KEY', "pk_test_poMIyXRk0ctfJGKxpJYeHa94")
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', "sk_test_nVVDnn3MEp769przNtUCPEuN")
stripe.api_key = STRIPE_SECRET_KEY

# Create your views here.
def payment_method_view(request):
    # if request.user.is_authenticated:
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        redirect('/cart/')

    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
            next_url = next_
    return render(request, 'billing/payment_method.html', {'publish_key': STRIPE_PUBLISH_KEY, 'next_url': next_url})

def payment_method_createview(request):
    if request.method == 'POST' and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({'message': 'Cannot find user'}, status_code = 401)
        token = request.POST.get('token')
        if token:
            # card = stripe.Customer.create_source(
            #     billing_profile.customer_id,
            #     source = token
            # )
            # new_card_obj = Card.objects.add_new(billing_profile = billing_profile, stripe_card_response = card)
            new_card_obj = Card.objects.add_new(billing_profile = billing_profile, token = token)
        return JsonResponse({'message': 'Success! Your card was added'})
    return HttpResponse("Error", status_code = 401)