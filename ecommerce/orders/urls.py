from django.urls import path

from .views import OrderListView, OrderDetailView, VerifyOwnership, GeneratePdf

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name = 'all-orders'),
    path('api/endpoint/verify/ownership/', VerifyOwnership.as_view(), name = 'verify-ownership'),
    path('<str:order_id>/', OrderDetailView.as_view(), name = 'single-order'),
    path('<str:order_id>/invoice/', GeneratePdf.as_view(), name = 'order-invoice'),
]