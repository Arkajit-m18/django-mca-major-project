from django.urls import path, re_path

from .views import AccountHomeView, AccountEmailActivateView, UserDetailUpdateView

app_name = 'accounts'

urlpatterns = [
    path('', AccountHomeView.as_view(), name = 'accounts_home'),
    path('details/', UserDetailUpdateView.as_view(), name = 'user-update'),
    re_path(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name = 'email_activate'),
    path('email/resend-activation/', AccountEmailActivateView.as_view(), name = 'resend-activation'),
]