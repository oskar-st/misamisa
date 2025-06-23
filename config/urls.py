from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import homepage, sklep, register_view, login_view, logout_view, profile_view, test_email, test_email_simple, verify_email

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('sklep/', sklep, name='sklep'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('test-email/', test_email, name='test_email'),
    path('test-email-simple/', test_email_simple, name='test_email_simple'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
