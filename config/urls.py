from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import homepage, sklep, register_view, login_view, logout_view, profile_view, verify_email
from .admin import admin_site
from shop.views import product_list_public, product_detail_public, cart_view, checkout_view

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', homepage, name='home'),
    path('admin/', admin_site.urls),
    path('shop/', include('shop.urls', namespace='shop')),
    path('sklep/', product_list_public, name='public_product_list'),
    path('produkt/<slug:slug>/', product_detail_public, name='public_product_detail'),
    path('koszyk/', cart_view, name='cart_view'),
    path('zamowienie/', checkout_view, name='checkout_view'),
    path('sukces/', lambda request: render(request, 'shop/order_success.html'), name='order_success'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
