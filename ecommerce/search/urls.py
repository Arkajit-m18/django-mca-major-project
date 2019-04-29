from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    path('', views.SearchProductView.as_view(), name = 'search_list'),
]