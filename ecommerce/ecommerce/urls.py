"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

from accounts.views import LoginView, RegisterView, GuestRegisterView
from . import views
from carts.views import cart_home, cart_detail_api_view, cart_quantity_api_view
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from billing.views import payment_method_view, payment_method_createview
from marketing.views import MarketingPreferenceView, MailchimpWebhookView
from orders.views import LibraryView

urlpatterns = [
    path('', views.home_page, name = 'home'),
    path('about/', views.about_page, name = 'about'),
    path('contacts/', views.contacts_page, name = 'contacts'),
    path('addresses/', include('addresses.urls', namespace = 'addresses')),
    # path('accounts/login/', RedirectView.as_view(url = '/login/')),
    path('accounts/', RedirectView.as_view(url = '/account')),
    path('account/', include('accounts.urls', namespace = 'accounts')),
    path('accounts/', include('accounts.passwords.urls')),
    path('login/', LoginView.as_view(), name = 'login'),
    path('analytics/', include('analytics.urls', namespace = 'analytics')),
    # path('login/', login_page, name = 'login'),
    path('register/guest/', GuestRegisterView.as_view(), name = 'guest_register'),
    # path('register/guest/', guest_register_view, name = 'guest_register'),
    path('checkout/address/create/', checkout_address_create_view, name = 'checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name = 'checkout_address_reuse'),
    path('api/cart/', cart_detail_api_view, name = 'api_cart'),
    path('api/cart/quantity/', cart_quantity_api_view, name = 'api_cart_quantity'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('billing/payment-method/', payment_method_view, name = 'billing-payment-method'),
    path('billing/payment-method/create/', payment_method_createview, name = 'billing-payment-method-endpoint'),
    path('register/', RegisterView.as_view(), name = 'register'),
    # path('register/', register_page, name = 'register'),
    path('products/', include('products.urls', namespace = 'products')),
    path('orders/', include('orders.urls', namespace = 'orders')),
    path('library/', LibraryView.as_view(), name = 'digital_library'),
    path('search/', include('search.urls', namespace = 'search')),
    path('cart/', include('carts.urls', namespace = 'carts')),
    path('settings/', RedirectView.as_view(url = '/account')),
    path('settings/email/', MarketingPreferenceView.as_view(), name = 'marketing_pref'),
    path('webhooks/mailchimp/', MailchimpWebhookView.as_view(), name = 'webhooks-mailchimp'),

    path('posts/', include('posts.urls', namespace = 'posts')),
    path('groups/', include('groups.urls', namespace = 'groups')),

    path('rooms/', include('rooms.urls', namespace = 'rooms')),
    path('chat/', include('chat.urls', namespace = 'chat')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
