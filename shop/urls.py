from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list_public, name='public_product_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail_public, name='public_product_detail'),
    # Optionally, admin-only product list:
    path('admin/', views.product_list, name='admin_product_list'),
    path('shop/', views.product_list_public, name='public_product_list_alt'),
] 