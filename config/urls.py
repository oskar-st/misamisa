from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from home.views import homepage, register_view, login_view, logout_view, profile_view, verify_email, resend_verification_email
from .admin import admin_site
from shop.views import product_list_public, product_detail_public, cart_view, checkout, place_order, order_success

# Import module manager to get module URLs
from modules.manager import module_manager

def downloads_view(request):
    """Simple view to serve the downloads page."""
    return render(request, 'downloads/index.html')

def category_or_product_view(request, slug):
    """Handle both category and product URLs dynamically."""
    from shop.models import Category, Product
    
    # First check if it's a category
    try:
        category = Category.objects.get(slug=slug, is_active=True)
        return product_list_public(request, category_slug=slug)
    except Category.DoesNotExist:
        # If not a category, check if it's a product
        try:
            product = Product.objects.get(slug=slug, is_active=True)
            return product_detail_public(request, slug=slug)
        except Product.DoesNotExist:
            # If neither exists, raise 404
            from django.http import Http404
            raise Http404("Page not found")

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', homepage, name='home'),
    path('admin/', admin_site.urls),
    path('shop/', include('shop.urls', namespace='shop')),
    path('modules/', include('modules.urls', namespace='modules')),
    path('cart/', cart_view, name='cart_view'),
    path('checkout/', checkout, name='checkout_view'),
    path('checkout/success/', order_success, name='checkout_success'),
    path('place-order/', place_order, name='place_order'),
    path('success/', order_success, name='order_success'),
    path('success/<int:order_id>/', order_success, name='order_success_with_id'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('downloads/', downloads_view, name='downloads'),
    # Combined category and product URLs - single pattern that handles both
    path('<slug:slug>/', category_or_product_view, name='category_or_product'),
]

# Add module URLs dynamically
module_manager.load_all_modules()
module_urls = module_manager.get_module_urls()
urlpatterns.extend(module_urls)

# Add downloads URL pattern for static files (ZIP downloads)
urlpatterns += static(settings.DOWNLOADS_URL, document_root=settings.DOWNLOADS_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
