"""
Module views for the module management system.
"""
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .manager import module_manager
import os
import zipfile
import tempfile
import shutil
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse
import json
from typing import Dict


def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def module_list(request: HttpRequest) -> HttpResponse:
    """Display list of all modules."""
    # Get modules by type
    modules_by_type = {
        'design': module_manager.get_modules_by_type('design'),
        'shipping': module_manager.get_modules_by_type('shipping'),
        'payment': module_manager.get_modules_by_type('payment'),
        'general': module_manager.get_modules_by_type('general'),
    }
    
    # Get all modules info
    all_modules = module_manager.get_all_modules_info()
    
    # Get installed modules
    installed_modules = module_manager.get_installed_modules()
    
    context = {
        'modules_by_type': modules_by_type,
        'all_modules': all_modules,
        'installed_modules': installed_modules,
    }
    return TemplateResponse(request, 'modules/module_list.html', context)


@login_required
@user_passes_test(is_admin)
def module_detail(request: HttpRequest, module_name: str) -> HttpResponse:
    """Display module details."""
    module_info = module_manager.get_module_info(module_name)
    if not module_info:
        messages.error(request, f'Module {module_name} not found.')
        return redirect('modules:module_list')
    
    context = {
        'module_info': module_info,
        'module_name': module_name,
        'installed_modules': module_manager.get_installed_modules(),
    }
    return TemplateResponse(request, 'modules/module_detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def install_module(request: HttpRequest, module_name: str) -> HttpResponse:
    """Install a module."""
    success = module_manager.install_module(module_name)
    
    if success:
        messages.success(request, f'Module {module_name} installed successfully.')
    else:
        messages.error(request, f'Failed to install module {module_name}.')
    
    return redirect('modules:module_list')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def uninstall_module(request: HttpRequest, module_name: str) -> HttpResponse:
    """Uninstall a module."""
    success = module_manager.uninstall_module(module_name)
    
    if success:
        messages.success(request, f'Module {module_name} uninstalled successfully.')
    else:
        messages.error(request, f'Failed to uninstall module {module_name}.')
    
    return redirect('modules:module_list')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def enable_module(request: HttpRequest, module_name: str) -> HttpResponse:
    """Enable a module."""
    success = module_manager.enable_module(module_name)
    
    if success:
        messages.success(request, f'Module {module_name} enabled successfully.')
    else:
        messages.error(request, f'Failed to enable module {module_name}.')
    
    return redirect('modules:module_list')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def disable_module(request: HttpRequest, module_name: str) -> HttpResponse:
    """Disable a module."""
    success = module_manager.disable_module(module_name)
    
    if success:
        messages.success(request, f'Module {module_name} disabled successfully.')
    else:
        messages.error(request, f'Failed to disable module {module_name}.')
    
    return redirect('modules:module_list')


@login_required
@user_passes_test(is_admin)
def module_config(request: HttpRequest, module_name: str) -> HttpResponse:
    """Configure a module."""
    module = module_manager.get_module(module_name)
    if not module:
        messages.error(request, f'Module {module_name} not found.')
        return redirect('modules:module_list')
    
    # Check if module has admin config template
    admin_config_template = module.get_admin_config()
    
    if not admin_config_template:
        messages.warning(request, f'Module {module_name} does not have configuration options.')
        return redirect('modules:module_detail', module_name=module_name)
    
    # Handle POST request for configuration updates
    if request.method == 'POST':
        try:
            # Get all form data dynamically (don't assume specific field names)
            config_data = {}
            for key, value in request.POST.items():
                if key != 'csrfmiddlewaretoken':  # Exclude CSRF token
                    config_data[key] = value.strip()
            
            # Validate that we have some configuration data
            if not config_data:
                messages.error(request, 'No configuration data provided.')
                return redirect('modules:module_config', module_name=module_name)
            
            # Save configuration
            config_file = os.path.join(settings.BASE_DIR, 'modules', 'config', f'{module_name}_config.json')
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            messages.success(request, f'Configuration saved successfully for {module_name}.')
            return redirect('modules:module_detail', module_name=module_name)
            
        except Exception as e:
            messages.error(request, f'Error saving configuration: {str(e)}')
            return redirect('modules:module_config', module_name=module_name)
    
    # Get existing configuration
    config = _get_module_config(module_name)
    
    context = {
        'module_info': module_manager.get_module_info(module_name),
        'module_name': module_name,
        'admin_config_template': admin_config_template,
        'config': config,
    }
    
    # Render the admin config template directly
    return render(request, admin_config_template, context)


def _save_module_config(module_name: str, config_data: dict) -> bool:
    """Save module configuration to database or file."""
    try:
        # Create modules config directory if it doesn't exist
        config_dir = os.path.join(settings.BASE_DIR, 'modules', 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Save to JSON file
        config_file = os.path.join(config_dir, f'{module_name}_config.json')
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Also update Django settings for immediate use
        _update_django_settings(module_name, config_data)
        
        return True
    except Exception as e:
        print(f"Error saving module config: {e}")
        return False


def _get_module_config(module_name: str) -> dict:
    """Get module configuration from database or file."""
    try:
        # Try to load from JSON file
        config_file = os.path.join(settings.BASE_DIR, 'modules', 'config', f'{module_name}_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading module config: {e}")
    
    # Return default configuration
    return {
        'name': '',
        'description': '',
        'version': '',
        'author': '',
        'category': '',
        'enabled': False,
        'test_mode': False
    }


def _update_django_settings(module_name: str, config_data: dict):
    """Update Django settings with module configuration."""
    try:
        # Generic module configuration update
        # Each module should handle its own settings in its install() method
        # This is just a fallback for basic configuration storage
        
        # Store module configuration in a generic way
        if not hasattr(settings, 'MODULE_CONFIGS'):
            settings.MODULE_CONFIGS = {}
        
        settings.MODULE_CONFIGS[module_name] = config_data
        
    except Exception as e:
        print(f"Error updating Django settings: {e}")


@login_required
@user_passes_test(is_admin)
def module_dashboard(request: HttpRequest) -> HttpResponse:
    """Module dashboard."""
    # Get all modules info
    all_modules = module_manager.get_all_modules_info()
    
    # Get payment modules
    payment_modules = module_manager.get_payment_modules()
    
    # Get shipping modules
    shipping_modules = module_manager.get_shipping_modules()
    
    # Get design modules
    design_modules = module_manager.get_design_modules()
    
    context = {
        'all_modules': all_modules,
        'payment_modules': payment_modules,
        'shipping_modules': shipping_modules,
        'design_modules': design_modules,
    }
    return TemplateResponse(request, 'modules/module_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def module_api(request: HttpRequest) -> JsonResponse:
    """Module API endpoint."""
    if request.method == 'GET':
        # Return module information
        module_manager.load_all_modules()
        modules_info = module_manager.get_all_modules_info()
        return JsonResponse({
            'modules': modules_info,
            'total': len(modules_info),
            'active': len([m for m in modules_info.values() if m['is_active']])
        })
    elif request.method == 'POST':
        # Handle module actions
        action = request.POST.get('action')
        module_name = request.POST.get('module_name')
        
        if not action or not module_name:
            return JsonResponse({'error': 'Missing action or module_name'}, status=400)
        
        if action == 'install':
            success = module_manager.install_module(module_name)
        elif action == 'uninstall':
            success = module_manager.uninstall_module(module_name)
        elif action == 'enable':
            success = module_manager.enable_module(module_name)
        elif action == 'disable':
            success = module_manager.disable_module(module_name)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({'success': success})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@permission_required('modules.add_module')
def module_upload(request: HttpRequest) -> TemplateResponse:
    """Upload a new module via ZIP file with standardized structure."""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('module_file')
        
        if not uploaded_file:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please select a module file to upload.'})
            messages.error(request, 'Please select a module file to upload.')
            return redirect('modules:upload')
        
        if not uploaded_file.name.endswith('.zip'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please upload a ZIP file containing the module.'})
            messages.error(request, 'Please upload a ZIP file containing the module.')
            return redirect('modules:upload')
        
        try:
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded file temporarily
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Extract ZIP file
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the module directory (it could be at root or in a subdirectory)
                module_root_dir = temp_dir
                extracted_items = os.listdir(temp_dir)
                
                # Look for a directory that contains the required module files
                for item in extracted_items:
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        # Check if this directory contains the required files
                        has_manifest = os.path.exists(os.path.join(item_path, 'manifest.json'))
                        has_module = os.path.exists(os.path.join(item_path, 'module.py'))
                        has_init = os.path.exists(os.path.join(item_path, '__init__.py'))
                        
                        if has_manifest and has_module and has_init:
                            module_root_dir = item_path
                            break
                
                # Validate the extracted structure
                validation_result = _validate_standardized_module_structure(module_root_dir)
                
                if not validation_result['valid']:
                    error_message = f"Invalid module structure: {'; '.join(validation_result['errors'])}"
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': error_message})
                    messages.error(request, error_message)
                    return redirect('modules:upload')
                
                # Get module name from manifest
                module_name = validation_result['module_name']
                manifest = validation_result['manifest']
                
                # Check for module conflicts
                modules_dir = os.path.join(settings.BASE_DIR, 'modules')
                target_dir = os.path.join(modules_dir, module_name)
                
                if os.path.exists(target_dir):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Module "{module_name}" already exists. Please remove it first.'})
                    messages.warning(request, f'Module "{module_name}" already exists. It will be overwritten.')
                    shutil.rmtree(target_dir)
                
                # Copy module to modules directory
                shutil.copytree(module_root_dir, target_dir)
                
                # Save uploaded ZIP for potential reinstallation
                zip_storage_path = os.path.join(modules_dir, f"{module_name}_module.zip")
                shutil.copy2(temp_file_path, zip_storage_path)
                
                # Get dependencies from manifest
                dependencies = manifest.get('install_requires', manifest.get('dependencies', []))
                if dependencies:
                    # Install each dependency
                    for dependency in dependencies:
                        print(f"Installing dependency: {dependency}")
                        venv_pip = os.path.join(settings.BASE_DIR, 'venv', 'bin', 'pip')
                        import subprocess
                        import sys
                        try:
                            if os.path.exists(venv_pip):
                                result = subprocess.run([
                                    venv_pip, 'install', dependency
                                ], capture_output=True, text=True, check=True)
                            else:
                                result = subprocess.run([
                                    sys.executable, '-m', 'pip', 'install', dependency
                                ], capture_output=True, text=True, check=True)
                            print(f"Dependency {dependency} installed successfully")
                        except Exception as dep_error:
                            error_msg = f"Failed to install dependency {dependency}: {str(dep_error)}"
                            print(error_msg)
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': False, 'message': error_msg})
                            messages.error(request, error_msg)
                            return redirect('modules:upload')
                else:
                    print(f"No dependencies listed for {module_name}")
                # Try loading the module again
                module_instance = module_manager.load_module(module_name)
                if module_instance:
                    install_success = module_manager.install_module(module_name)
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        if install_success:
                            return JsonResponse({
                                'success': True, 
                                'message': f'Module "{module_name}" uploaded and installed successfully!',
                                'module_info': {
                                    'name': module_name,
                                    'version': manifest.get('version', '1.0.0'),
                                    'description': manifest.get('description', ''),
                                    'type': manifest.get('type', 'general')
                                }
                            })
                        else:
                            return JsonResponse({
                                'success': True, 
                                'message': f'Module "{module_name}" uploaded successfully but installation failed.'
                            })
                    messages.success(request, f'Module "{module_name}" uploaded and loaded successfully!')
                    if install_success:
                        messages.success(request, f'Module "{module_name}" installed successfully!')
                    else:
                        messages.warning(request, f'Module "{module_name}" loaded but installation failed.')
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Failed to load module "{module_name}".'})
                    messages.error(request, f'Failed to load module "{module_name}".')
                    return redirect('modules:upload')
        except zipfile.BadZipFile:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid ZIP file. Please check the file format.'})
            messages.error(request, 'Invalid ZIP file. Please check the file format.')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error uploading module: {str(e)}'})
            messages.error(request, f'Error uploading module: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect': reverse('modules:module_list')})
        return redirect('modules:module_list')
    
    context = {
        'title': 'Upload Module'
    }
    
    return TemplateResponse(request, 'modules/module_upload.html', context)


@login_required
@permission_required('modules.change_module')
def module_install(request: HttpRequest, module_name: str) -> JsonResponse:
    """Install a specific module."""
    try:
        success = module_manager.install_module(module_name)
        if success:
            return JsonResponse({'success': True, 'message': f'Module "{module_name}" installed successfully!'})
        else:
            return JsonResponse({'success': False, 'message': f'Failed to install module "{module_name}".'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@permission_required('modules.delete_module')
def module_uninstall(request: HttpRequest, module_name: str) -> JsonResponse:
    """Uninstall a specific module."""
    try:
        success = module_manager.uninstall_module(module_name)
        if success:
            return JsonResponse({'success': True, 'message': f'Module "{module_name}" uninstalled successfully!'})
        else:
            return JsonResponse({'success': False, 'message': f'Failed to uninstall module "{module_name}".'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@permission_required('modules.delete_module')
def module_complete_remove(request: HttpRequest, module_name: str) -> JsonResponse:
    """Completely remove a module from the system.
    
    This will:
    1. Uninstall the module
    2. Remove all database records
    3. Delete all module files
    4. Clean up registry entries
    5. Remove the uploaded ZIP file
    """
    try:
        success = module_manager.purge_module(module_name)
        
        if success:
            return JsonResponse({
                'success': True, 
                'message': f'Module "{module_name}" completely purged from the system!'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': f'Failed to completely purge module "{module_name}".'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def complete_remove_module(request: HttpRequest, module_name: str) -> HttpResponse:
    """Complete module removal via form submission."""
    try:
        success = module_manager.purge_module(module_name)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if success:
                return JsonResponse({
                    'success': True, 
                    'message': f'Module {module_name} completely purged from the system.'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': f'Failed to completely purge module {module_name}.'
                })
        
        if success:
            messages.success(request, f'Module {module_name} completely purged from the system.')
        else:
            messages.error(request, f'Failed to completely purge module {module_name}.')
        
        return redirect('modules:module_list')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': f'Error purging module: {str(e)}'
            })
        
        messages.error(request, f'Error purging module: {str(e)}')
        return redirect('modules:module_list')


def _validate_standardized_module_structure(module_dir: str) -> Dict:
    """
    Validate that the extracted module has the standardized structure.
    
    Returns:
        Dict with 'valid' (bool), 'errors' (list), 'module_name' (str), 'manifest' (dict)
    """
    result = {
        'valid': False,
        'errors': [],
        'module_name': None,
        'manifest': None
    }
    
    # Check for required files
    required_files = ['manifest.json', 'module.py', '__init__.py']
    for file_name in required_files:
        file_path = os.path.join(module_dir, file_name)
        if not os.path.exists(file_path):
            result['errors'].append(f"Missing required file: {file_name}")
    
    if result['errors']:
        return result
    
    # Validate manifest.json
    try:
        manifest_path = os.path.join(module_dir, 'manifest.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check required manifest fields
        required_manifest_fields = ['name', 'version', 'description', 'author', 'type']
        for field in required_manifest_fields:
            if field not in manifest:
                result['errors'].append(f"Missing required manifest field: {field}")
        
        if result['errors']:
            return result
        
        # Validate module name
        module_name = manifest['name']
        if not module_name or not module_name.replace('_', '').replace('-', '').isalnum():
            result['errors'].append("Invalid module name. Use only letters, numbers, underscores, and hyphens.")
        
        if result['errors']:
            return result
        
        result['module_name'] = module_name
        result['manifest'] = manifest
        
    except json.JSONDecodeError as e:
        result['errors'].append(f"Invalid manifest.json: {str(e)}")
        return result
    except Exception as e:
        result['errors'].append(f"Error reading manifest.json: {str(e)}")
        return result
    
    # Validate module.py
    try:
        module_path = os.path.join(module_dir, 'module.py')
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for module class definition
        if 'class' not in content:
            result['errors'].append("module.py must contain a class definition")
        
        # Check for base class inheritance
        base_classes = ['BaseModule', 'PaymentModuleBase', 'ShippingModuleBase', 'DesignModuleBase']
        has_base_class = any(base_class in content for base_class in base_classes)
        if not has_base_class:
            result['errors'].append("module.py must inherit from a base module class")
        
        if result['errors']:
            return result
            
    except Exception as e:
        result['errors'].append(f"Error reading module.py: {str(e)}")
        return result
    
    # Validate directory structure
    expected_dirs = [
        'templates',
        f'templates/{module_name}',
    ]
    
    # Static directories are optional
    optional_dirs = [
        'static',
        f'static/{module_name}'
    ]
    
    for dir_name in expected_dirs:
        dir_path = os.path.join(module_dir, dir_name)
        if not os.path.exists(dir_path):
            result['errors'].append(f"Missing expected directory: {dir_name}")
    
    # Check optional directories and warn if missing
    for dir_name in optional_dirs:
        dir_path = os.path.join(module_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"Warning: Optional directory missing: {dir_name}")
    
    if result['errors']:
        return result
    
    # Check for template files based on module type
    module_type = manifest.get('type', 'general')
    if module_type == 'payment':
        payment_form_path = os.path.join(module_dir, f'templates/{module_name}/payment_form.html')
        if not os.path.exists(payment_form_path):
            result['errors'].append(f"Payment modules must include templates/{module_name}/payment_form.html")
    
    # Check for admin config template
    admin_config_path = os.path.join(module_dir, f'templates/{module_name}/admin/config.html')
    if not os.path.exists(admin_config_path):
        result['errors'].append(f"Missing admin configuration template: templates/{module_name}/admin/config.html")
    
    # If no errors, mark as valid
    if not result['errors']:
        result['valid'] = True
    
    return result


def _validate_module_structure(module_dir: str, module_name: str) -> bool:
    """Validate that the extracted module has the correct structure."""
    required_files = ['module.py']
    optional_dirs = ['templates', 'static', 'migrations']
    
    # First, check if module.py is directly in the module_dir
    module_file = os.path.join(module_dir, 'module.py')
    if os.path.exists(module_file):
        # Direct structure: module_dir/module.py
        module_root = module_dir
    else:
        # Nested structure: module_dir/module_name/module.py
        module_root = os.path.join(module_dir, module_name)
        module_file = os.path.join(module_root, 'module.py')
        if not os.path.exists(module_file):
            return False
    
    # Check for required files in the module root
    for file_name in required_files:
        file_path = os.path.join(module_root, file_name)
        if not os.path.exists(file_path):
            return False
    
    # Check module.py contains a valid module class
    try:
        with open(module_file, 'r') as f:
            content = f.read()
            if 'class' not in content or 'ModuleBase' not in content:
                return False
    except Exception:
        return False
    
    return True 


def module_download(request, module_name):
    """Download a module ZIP file"""
    if not request.user.is_staff:
        return redirect('admin:login')
    
    # Check if the module ZIP exists
    zip_path = os.path.join(settings.BASE_DIR, 'modules', f'{module_name}_module.zip')
    
    if not os.path.exists(zip_path):
        messages.error(request, f'Module ZIP file for {module_name} not found.')
        return redirect('modules:list')
    
    # Serve the file for download
    with open(zip_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{module_name}_module.zip"'
        return response 

def _get_default_config():
    """Get default configuration for modules."""
    # Return empty dict - let each module define its own configuration structure
    return {} 