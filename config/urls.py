from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.generic import RedirectView
from django.urls import URLResolver, URLPattern
from django.http import Http404, JsonResponse
from home.views import homepage, register_view, login_view, logout_view, profile_view, verify_email, resend_verification_email, contact_view, about_view, terms_view, privacy_view
from .admin import admin_site
from shop.views import product_list_public, product_detail_public, cart_view, checkout, place_order, order_success
import os
import json
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Import module manager to get module URLs
from modules.manager import module_manager

def downloads_view(request):
    """Simple view to serve the downloads page."""
    return render(request, 'downloads/index.html', {}, content_type='text/html')

def downloads_list_api(request):
    """API endpoint to list all files in downloads folder."""
    downloads_dir = Path(settings.BASE_DIR) / 'downloads'
    files = []
    
    if downloads_dir.exists():
        for file_path in downloads_dir.iterdir():
            if file_path.is_file():  # Only include files, not directories
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime * 1000,  # Convert to milliseconds for JavaScript
                })
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return JsonResponse(files, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def downloads_upload_api(request):
    """API endpoint to upload any files to downloads folder."""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Security check - prevent dangerous file types
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension in dangerous_extensions:
            return JsonResponse({'error': f'File type {file_extension} is not allowed for security reasons'}, status=400)
        
        # Save to downloads directory
        downloads_dir = Path(settings.BASE_DIR) / 'downloads'
        downloads_dir.mkdir(exist_ok=True)
        
        file_path = downloads_dir / uploaded_file.name
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        return JsonResponse({'success': True, 'filename': uploaded_file.name})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def downloads_delete_api(request):
    """API endpoint to delete any files from downloads folder."""
    try:
        data = json.loads(request.body)
        filename = data.get('filename')
        
        if not filename:
            return JsonResponse({'error': 'No filename provided'}, status=400)
        
        # Security check - prevent dangerous file types
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
        file_extension = Path(filename).suffix.lower()
        if file_extension in dangerous_extensions:
            return JsonResponse({'error': f'File type {file_extension} is not allowed for security reasons'}, status=400)
        
        # Prevent directory traversal
        if '..' in filename or '/' in filename:
            return JsonResponse({'error': 'Invalid filename'}, status=400)
        
        downloads_dir = Path(settings.BASE_DIR) / 'downloads'
        file_path = downloads_dir / filename
        
        if not file_path.exists():
            return JsonResponse({'error': 'File not found'}, status=404)
        
        # Delete the file
        file_path.unlink()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
    path('sklep/', include('shop.urls', namespace='shop')),
    # Redirect old /shop/ URLs to /sklep/ for backward compatibility
    path('shop/<path:remaining>', RedirectView.as_view(url='/sklep/%(remaining)s', permanent=True)),
    path('shop/', RedirectView.as_view(url='/sklep/', permanent=True)),
    path('modules/', include('modules.urls', namespace='modules')),
    path('', include('accounts.urls', namespace='accounts')),  # Include accounts URLs
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
    path('contact/', contact_view, name='contact'),
    path('about/', about_view, name='about'),
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('downloads/', downloads_view, name='downloads'),
    path('downloads/list/', downloads_list_api, name='downloads_list'),
    path('downloads/upload/', downloads_upload_api, name='downloads_upload'),
    path('downloads/delete/', downloads_delete_api, name='downloads_delete'),
    # Combined category and product URLs - single pattern that handles both
    path('<slug:slug>/', category_or_product_view, name='category_or_product'),
]

# Add module URLs dynamically
module_manager.load_all_modules()

# Add module URLs with proper namespacing
for module_name, module in module_manager.discovered_modules.items():
    if module.is_enabled:
        module_urls = module.get_urls()
        if module_urls:
            # Include the module's URLs with its namespace
            from django.urls import include, path
            urlpatterns.append(
                path(f'modules/{module_name}/', include((module_urls, module_name), namespace=module_name))
            )

# Add downloads URL pattern for static files (ZIP downloads)
urlpatterns += static(settings.DOWNLOADS_URL, document_root=settings.DOWNLOADS_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
