from django.urls import path

from .views import AddressUpdateView, AddressCreateView

app_name = 'addresses'

urlpatterns = [
    path('create/', AddressCreateView.as_view(), name = 'create_address'),
    path('update/', AddressUpdateView.as_view(), name = 'update_address'),
]