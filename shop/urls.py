from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list_public, name='public_product_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    # Product URLs are now handled at root level in main urls.py
    path('api/update-cart/', views.update_cart_ajax, name='update_cart_ajax'),
    path('api/cart/batch/', views.update_cart_batch, name='update_cart_batch'),
    # Optionally, admin-only product list:
    path('admin/', views.product_list, name='admin_product_list'),
] 