"""
URL patterns for module management.
"""
from django.urls import path
from . import views
from .manager import module_manager

app_name = 'modules'

urlpatterns = [
    # Module management
    path('', views.module_list, name='module_list'),
    path('upload/', views.module_upload, name='upload'),
    path('<str:module_name>/', views.module_detail, name='module_detail'),
    path('<str:module_name>/install/', views.install_module, name='install_module'),
    path('<str:module_name>/uninstall/', views.uninstall_module, name='uninstall_module'),
    path('<str:module_name>/enable/', views.enable_module, name='enable_module'),
    path('<str:module_name>/disable/', views.disable_module, name='disable_module'),
    path('<str:module_name>/config/', views.module_config, name='module_config'),
    path('<str:module_name>/complete-remove/', views.complete_remove_module, name='complete_remove_module'),
    path('<str:module_name>/download/', views.module_download, name='module_download'),
    
    # AJAX actions
    path('install/<str:module_name>/', views.module_install, name='install'),
    path('uninstall/<str:module_name>/', views.module_uninstall, name='uninstall'),
    path('delete/<str:module_name>/', views.module_complete_remove, name='delete'),
    path('complete-remove/<str:module_name>/', views.module_complete_remove, name='complete_remove'),
    
    # API endpoints
    path('api/', views.module_api, name='module_api'),
] 