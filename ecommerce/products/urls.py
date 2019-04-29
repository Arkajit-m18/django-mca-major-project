from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name = 'all_products'),
    path('history/', views.UserProductHistoryView.as_view(), name = 'products-history'),
    path('featured/', views.ProductFeaturedListView.as_view(), name = 'featured_products'),
    path('<slug:slug>/', views.ProductSlugDetailView.as_view(), name = 'single_product'),
    path('<slug:slug>/<int:pk>/', views.ProductDownloadView.as_view(), name = 'download'),
    path('featured/<slug:slug>/', views.ProductSlugFeaturedDetailView.as_view(), name = 'single_featured'),

    
    # path('<int:pk>/', views.ProductDetailView.as_view(), name = 'single_product'),
    # path('featured/<int:pk>/', views.ProductFeaturedDetailView.as_view(), name = 'single_featured'),
]