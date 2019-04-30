from django.urls import path

from .views import SalesView, SalesAjaxView

app_name = 'analytics'

urlpatterns = [
    path('sales/', SalesView.as_view(), name = 'sales'),
    path('api/sales/data/', SalesAjaxView.as_view(), name = 'sales_data'),
]