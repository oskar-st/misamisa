"""
Module manager for discovering, loading, and managing modules.
"""
import os
import importlib
import inspect
import shutil
import json
from typing import Dict, List, Optional, Type, Any
from django.conf import settings
from django.apps import apps
from django.urls import path, include
from django.contrib import admin
from .base import BaseModule, PaymentModuleBase, ShippingModuleBase, DesignModuleBase, ModuleManifest
import shutil
import json


class ModuleManager:
    """Manages module discovery, loading, and registration."""
    
    def __init__(self):
        """Initialize the module manager."""
        self.modules_path = os.path.join(settings.BASE_DIR, "modules")
        self.discovered_modules: Dict[str, BaseModule] = {}
        self._uninstalled_modules_file = os.path.join(settings.BASE_DIR, "uninstalled_modules.json")
        self.load_all_modules()
    
    def _get_uninstalled_modules(self) -> set:
        """Get list of uninstalled modules from file."""
        try:
            if os.path.exists(self._uninstalled_modules_file):
                with open(self._uninstalled_modules_file, 'r') as f:
                    return set(json.load(f))
        except Exception:
            pass
        return set()
    
    def _save_uninstalled_modules(self, uninstalled_modules: set):
        """Save list of uninstalled modules to file."""
        try:
            with open(self._uninstalled_modules_file, 'w') as f:
                json.dump(list(uninstalled_modules), f)
        except Exception:
            pass
    
    def discover_modules(self) -> List[str]:
        """Discover available modules in the modules directory."""
        discovered = []
        
        if not os.path.exists(self.modules_path):
            return discovered
        
        for item in os.listdir(self.modules_path):
            module_path = os.path.join(self.modules_path, item)
            
            # Check if it's a directory and contains a module.py file
            if os.path.isdir(module_path):
                module_file = os.path.join(module_path, 'module.py')
                manifest_file = os.path.join(module_path, 'manifest.json')
                
                # Check for both module.py and manifest.json
                if os.path.exists(module_file) and os.path.exists(manifest_file):
                    discovered.append(item)
        
        return discovered
    
    def load_module(self, module_name: str) -> Optional[BaseModule]:
        """Load a specific module by name."""
        try:
            module_path = os.path.join(self.modules_path, module_name)
            
            # Validate module structure
            validation_errors = self._validate_module_structure(module_path)
            if validation_errors:
                print(f"Module {module_name} validation errors: {validation_errors}")
                return None
            
            # Check and install dependencies before importing
            manifest_path = os.path.join(module_path, 'manifest.json')
            if os.path.exists(manifest_path):
                try:
                    manifest = ModuleManifest.from_file(manifest_path)
                    if manifest.install_requires:
                        print(f"Installing dependencies for {module_name}: {manifest.install_requires}")
                        self._install_dependencies(manifest.install_requires)
                except Exception as e:
                    print(f"Warning: Could not install dependencies for {module_name}: {e}")
            
            # Try to load the module
            try:
                module = self._load_module(module_name, module_path)
                if module:
                    self.discovered_modules[module_name] = module
                    print(f"✅ Module {module_name} loaded successfully")
                    return module
                else:
                    print(f"❌ Failed to load module {module_name}")
                    return None
                    
            except ImportError as e:
                print(f"❌ Import error for {module_name}: {e}")
                return None
            except Exception as e:
                print(f"❌ Error loading {module_name}: {e}")
                return None
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
            return None
    
    def _validate_module_structure(self, module_path: str) -> List[str]:
        """Validate module directory structure."""
        errors = []
        
        # Check required files
        required_files = ['module.py', '__init__.py', 'manifest.json']
        for file in required_files:
            if not os.path.exists(os.path.join(module_path, file)):
                errors.append(f"Missing required file: {file}")
        
        # Check manifest.json
        manifest_path = os.path.join(module_path, 'manifest.json')
        if os.path.exists(manifest_path):
            try:
                manifest = ModuleManifest.from_file(manifest_path)
                manifest_errors = manifest.validate()
                errors.extend(manifest_errors)
            except ValueError as e:
                errors.append(f"Invalid manifest.json: {e}")
        
        return errors
    
    def load_all_modules(self) -> Dict[str, BaseModule]:
        """Load all discovered modules."""
        discovered = self.discover_modules()
        loaded = {}
        uninstalled_modules = self._get_uninstalled_modules()
        
        for module_name in discovered:
            # Skip loading modules that are marked as uninstalled
            if module_name in uninstalled_modules:
                print(f"Skipping uninstalled module: {module_name}")
                continue
                
            module_instance = self.load_module(module_name)
            if module_instance:
                loaded[module_name] = module_instance
                # Mark as installed if it's discovered and not uninstalled
                module_instance.is_installed = True
                module_instance.is_enabled = True
        
        return loaded
    
    def get_module_urls(self) -> List:
        """Get all module URLs for active modules."""
        urls = []
        
        for module_name, module in self.discovered_modules.items():
            if module.is_enabled:
                module_urls = module.get_urls()
                if module_urls:
                    # Add module prefix to each URL pattern
                    for url_pattern in module_urls:
                        # Get the pattern string from the URLPattern object
                        if hasattr(url_pattern, 'pattern'):
                            # For Django 4.0+ URLPattern objects
                            if hasattr(url_pattern.pattern, '_route'):
                                pattern_str = url_pattern.pattern._route
                            elif hasattr(url_pattern.pattern, 'regex'):
                                # Fallback: use regex pattern, remove leading ^ if present
                                pattern_str = url_pattern.pattern.regex.pattern
                                if pattern_str.startswith('^'):
                                    pattern_str = pattern_str[1:]
                            else:
                                # Try to get the pattern string directly
                                pattern_str = str(url_pattern.pattern)
                        else:
                            # Fallback for older Django versions
                            pattern_str = str(url_pattern)
                        
                        # Clean up the pattern string
                        pattern_str = pattern_str.lstrip("/")
                        
                        # Create new URL pattern with module prefix
                        from django.urls import path
                        new_pattern = path(f'{module_name}/{pattern_str}', 
                                         url_pattern.callback, 
                                         name=f'{module_name}_{url_pattern.name}')
                        urls.append(new_pattern)
        
        return urls
    
    def get_active_modules(self) -> Dict[str, BaseModule]:
        """Get all active (enabled) modules."""
        return {
            name: module 
            for name, module in self.discovered_modules.items() 
            if module.is_enabled
        }
    
    def get_installed_modules(self) -> Dict[str, BaseModule]:
        """Get all installed modules."""
        return {
            name: module 
            for name, module in self.discovered_modules.items() 
            if module.is_installed
        }
    
    def get_payment_modules(self) -> Dict[str, BaseModule]:
        """Get all payment modules."""
        payment_modules = {}
        for name, module in self.discovered_modules.items():
            if (isinstance(module, PaymentModuleBase) and 
                module.is_installed and module.is_enabled):
                payment_modules[name] = module
        return payment_modules
    
    def get_shipping_modules(self) -> Dict[str, BaseModule]:
        """Get all shipping modules."""
        shipping_modules = {}
        for name, module in self.discovered_modules.items():
            if (isinstance(module, ShippingModuleBase) and 
                module.is_installed and module.is_enabled):
                shipping_modules[name] = module
        return shipping_modules
    
    def get_design_modules(self) -> Dict[str, BaseModule]:
        """Get all design modules."""
        design_modules = {}
        for name, module in self.discovered_modules.items():
            if (isinstance(module, DesignModuleBase) and 
                module.is_installed and module.is_enabled):
                design_modules[name] = module
        return design_modules
    
    def get_module_templates(self) -> List[str]:
        """Get all module template directories."""
        templates = []
        active_modules = self.get_active_modules()
        
        for module_name, module in active_modules.items():
            module_templates = module.get_templates()
            templates.extend(module_templates)
        
        return templates
    
    def get_module_static_files(self) -> List[str]:
        """Get all module static file directories."""
        static_files = []
        active_modules = self.get_active_modules()
        
        for module_name, module in active_modules.items():
            module_static = module.get_static_files()
            static_files.extend(module_static)
        
        return static_files
    
    def install_module(self, module_name: str) -> bool:
        """Install a specific module."""
        if module_name not in self.discovered_modules:
            return False
        
        module = self.discovered_modules[module_name]
        try:
            # Step 1: Install dependencies if manifest exists
            if module.manifest and module.manifest.install_requires:
                print(f"Installing dependencies for {module_name}: {module.manifest.install_requires}")
                self._install_dependencies(module.manifest.install_requires)
            
            # Step 2: Install the module
            success = module.install()
            if success:
                module.is_installed = True
                self.mark_module_installed(module_name)
            return success
        except Exception as e:
            print(f"Failed to install module {module_name}: {e}")
            return False
    
    def _install_dependencies(self, dependencies: List[str]) -> bool:
        """Install Python package dependencies using pip."""
        import subprocess
        import sys
        import os
        
        try:
            # Use the virtual environment's pip if available
            venv_pip = os.path.join(settings.BASE_DIR, 'venv', 'bin', 'pip')
            if os.path.exists(venv_pip):
                pip_command = venv_pip
            else:
                pip_command = [sys.executable, '-m', 'pip']
            
            for dependency in dependencies:
                print(f"Installing dependency: {dependency}")
                if isinstance(pip_command, str):
                    result = subprocess.run([
                        pip_command, 'install', dependency
                    ], capture_output=True, text=True, check=True)
                else:
                    result = subprocess.run([
                        *pip_command, 'install', dependency
                    ], capture_output=True, text=True, check=True)
                print(f"Successfully installed {dependency}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def uninstall_module(self, module_name: str) -> bool:
        """Uninstall a module but preserve the uploaded ZIP file for potential reinstallation."""
        print(f"Uninstalling module: {module_name}")
        
        try:
            # Step 1: Uninstall the module if it's installed
            print("Step 1: Uninstalling module", module_name)
            module = self.get_module(module_name)
            if module:
                module.uninstall()
            
            # Step 2: Clean up database records
            print("Step 2: Cleaning up database records for", module_name)
            self._cleanup_database_records(module_name)
            
            # Step 3: Remove from registry
            print("Step 3: Removing", module_name, "from registry")
            if module_name in self.discovered_modules:
                del self.discovered_modules[module_name]
            
            # Step 4: Remove module files
            print("Step 4: Removing module files for", module_name)
            module_dir = os.path.join(self.modules_path, module_name)
            if os.path.exists(module_dir):
                shutil.rmtree(module_dir)
                print(f"Removed module directory: {module_dir}")
            
            # Step 5: Check for uploaded ZIP file
            print("Step 5: Checking for uploaded ZIP file for", module_name)
            zip_path = os.path.join(self.modules_path, f'{module_name}_module.zip')
            if os.path.exists(zip_path):
                print(f"Found uploaded ZIP file: {zip_path}")
                print("ZIP file preserved for potential reinstallation")
            else:
                # Also check in MEDIA_ROOT/modules with .zip suffix (legacy location)
                zip_path_legacy = os.path.join(settings.MEDIA_ROOT, 'modules', f'{module_name}.zip')
                if os.path.exists(zip_path_legacy):
                    os.remove(zip_path_legacy)
                    print(f"Removed legacy uploaded ZIP file: {zip_path_legacy}")
                else:
                    print("No uploaded ZIP file found for", module_name)
            
            # Step 6: Clear module cache
            print("Step 6: Clearing module cache for", module_name)
            self._clear_module_cache(module_name)
            
            # Step 6.5: Remove Stripe keys from .env if this is the Stripe module
            if module_name == 'stripe_payment':
                print("Step 6.5: Removing Stripe keys from .env file")
                self._remove_stripe_keys_from_env()
            
            # Step 7: Mark as uninstalled
            self.mark_module_uninstalled(module_name)
            
            print(f"✅ Module {module_name} completely removed from the system")
            return True
            
        except Exception as e:
            print(f"❌ Error uninstalling module {module_name}: {e}")
            return False
    
    def purge_module(self, module_name: str) -> bool:
        """Completely purge a module including uploaded ZIP file.
        
        IMPORTANT: This function should NEVER touch the downloads folder.
        The downloads folder is for user-created/downloaded ZIP files and should
        remain completely separate from module installation/uninstallation.
        """
        print(f"Starting complete removal of module: {module_name}")
        
        try:
            # Step 1: Uninstall the module if it's installed
            print("Step 1: Uninstalling module", module_name)
            module = self.get_module(module_name)
            if module:
                module.uninstall()
            
            # Step 2: Clean up database records
            print("Step 2: Cleaning up database records for", module_name)
            self._cleanup_database_records(module_name)
            
            # Step 3: Remove from registry
            print("Step 3: Removing", module_name, "from registry")
            if module_name in self.discovered_modules:
                del self.discovered_modules[module_name]
            
            # Step 4: Remove module files
            print("Step 4: Removing module files for", module_name)
            module_dir = os.path.join(self.modules_path, module_name)
            if os.path.exists(module_dir):
                shutil.rmtree(module_dir)
                print(f"Removed module directory: {module_dir}")
            
            # Step 5: Remove uploaded ZIP file (NOT downloads folder)
            print("Step 5: Checking for uploaded ZIP file for", module_name)
            # Check in modules directory with _module.zip suffix (as saved by upload function)
            zip_path = os.path.join(self.modules_path, f'{module_name}_module.zip')
            if os.path.exists(zip_path):
                os.remove(zip_path)
                print(f"Removed uploaded ZIP file: {zip_path}")
            else:
                # Also check in MEDIA_ROOT/modules with .zip suffix (legacy location)
                zip_path_legacy = os.path.join(settings.MEDIA_ROOT, 'modules', f'{module_name}.zip')
                if os.path.exists(zip_path_legacy):
                    os.remove(zip_path_legacy)
                    print(f"Removed legacy uploaded ZIP file: {zip_path_legacy}")
                else:
                    print("No uploaded ZIP file found for", module_name)
            
            # Step 6: Clear module cache
            print("Step 6: Clearing module cache for", module_name)
            self._clear_module_cache(module_name)
            
            # Step 7: Comprehensive cleanup of any remaining files
            print("Step 7: Comprehensive cleanup of any remaining files")
            self._cleanup_module_remnants(module_name)
            
            # Step 8: Remove configuration files
            print("Step 8: Removing configuration files for", module_name)
            config_dir = os.path.join(self.modules_path, 'config')
            config_file = os.path.join(config_dir, f'{module_name}_config.json')
            if os.path.exists(config_file):
                os.remove(config_file)
                print(f"Removed configuration file: {config_file}")
            else:
                print(f"No configuration file found for {module_name}")
            
            # Step 8.5: Remove Stripe keys from .env if this is the Stripe module
            if module_name == 'stripe_payment':
                print("Step 8.5: Removing Stripe keys from .env file")
                self._remove_stripe_keys_from_env()
            
            # Step 9: Mark as uninstalled
            self.mark_module_uninstalled(module_name)
            
            print(f"✅ Module {module_name} completely removed from the system")
            return True
            
        except Exception as e:
            print(f"❌ Error purging module {module_name}: {e}")
            return False
    
    def enable_module(self, module_name: str) -> bool:
        """Enable a module."""
        if module_name not in self.discovered_modules:
            return False
        
        module = self.discovered_modules[module_name]
        try:
            success = module.enable()
            if success:
                module.is_enabled = True
            return success
        except Exception as e:
            print(f"Failed to enable module {module_name}: {e}")
            return False
    
    def disable_module(self, module_name: str) -> bool:
        """Disable a module."""
        if module_name not in self.discovered_modules:
            return False
        
        module = self.discovered_modules[module_name]
        try:
            success = module.disable()
            if success:
                module.is_enabled = False
            return success
        except Exception as e:
            print(f"Failed to disable module {module_name}: {e}")
            return False
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Get information about a specific module."""
        if module_name not in self.discovered_modules:
            return None
        
        module = self.discovered_modules[module_name]
        info = {
            'name': module.module_name,
            'type': module.module_type,
            'version': module.module_version,
            'description': module.module_description,
            'is_installed': module.is_installed,
            'is_enabled': module.is_enabled,
            'is_active': module.is_enabled,  # Alias for compatibility
            'has_manifest': module.has_manifest,
        }
        
        if module.manifest:
            info.update({
                'author': module.manifest.author,
                'dependencies': module.manifest.dependencies,
                'install_requires': module.manifest.install_requires,
                'admin_config': module.manifest.admin_config,
                'migrations': module.manifest.migrations,
                'is_configurable': module.manifest.admin_config,  # For module_detail.html
                'has_admin_config': module.manifest.admin_config,  # For module_list.html
            })
        
        return info
    
    def get_all_modules_info(self) -> Dict[str, Dict]:
        """Get information about all modules."""
        modules_info = {}
        for module_name in self.discovered_modules:
            info = self.get_module_info(module_name)
            if info:
                modules_info[module_name] = info
        return modules_info
    
    def get_modules_by_type(self, module_type: str) -> Dict[str, Dict]:
        """Get modules by type."""
        modules_info = {}
        for module_name, module in self.discovered_modules.items():
            if module.module_type == module_type:
                info = self.get_module_info(module_name)
                if info:
                    modules_info[module_name] = info
        return modules_info
    
    def _cleanup_database_records(self, module_name: str):
        """Clean up database records for a module."""
        # This would need to be implemented based on your specific database structure
        # For now, we'll just print a warning
        print(f"Warning: Database cleanup for {module_name} not implemented")
    
    def _clear_module_cache(self, module_name: str):
        """Clear Python cache for a module."""
        try:
            # Clear Python cache files
            cache_dirs = [
                os.path.join(self.modules_path, module_name, '__pycache__'),
                os.path.join(self.modules_path, '__pycache__'),
            ]
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                    print(f"Cleared cache for {cache_dir}")
            
            # Clear specific module cache
            import sys
            module_key = f"modules.{module_name}"
            if module_key in sys.modules:
                del sys.modules[module_key]
                print(f"Cleared cache for {module_key}")
            
        except Exception as e:
            print(f"Warning: Could not clear cache for {module_name}: {e}")
    
    def _cleanup_module_remnants(self, module_name: str):
        """Clean up any remaining files or references for a module.
        
        IMPORTANT: This function should NEVER touch the downloads folder.
        Only cleans up files in modules/ and MEDIA_ROOT/modules/ directories.
        """
        try:
            # Check for ZIP files in various locations (NOT downloads folder)
            zip_locations = [
                os.path.join(self.modules_path, f'{module_name}_module.zip'),
                os.path.join(self.modules_path, f'{module_name}.zip'),
                os.path.join(settings.MEDIA_ROOT, 'modules', f'{module_name}.zip'),
                os.path.join(settings.MEDIA_ROOT, 'modules', f'{module_name}_module.zip'),
            ]
            
            for zip_path in zip_locations:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    print(f"Removed remnant ZIP file: {zip_path}")
            
            # Check for any other module-specific files
            module_files = [
                os.path.join(self.modules_path, f'{module_name}_backup.zip'),
                os.path.join(self.modules_path, f'{module_name}_old.zip'),
            ]
            
            for file_path in module_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Removed remnant file: {file_path}")
                    
        except Exception as e:
            print(f"Warning: Could not clean up remnants for {module_name}: {e}")
    
    def _remove_stripe_keys_from_env(self):
        """Remove Stripe keys from .env file."""
        try:
            env_file = os.path.join(settings.BASE_DIR, '.env')
            
            if not os.path.exists(env_file):
                return
            
            # Read existing .env file
            with open(env_file, 'r') as f:
                env_lines = f.readlines()
            
            # Filter out Stripe-related lines
            updated_lines = []
            in_stripe_section = False
            
            for line in env_lines:
                if line.strip().startswith('# Stripe Payment Module Settings'):
                    in_stripe_section = True
                    continue
                elif in_stripe_section and (line.strip().startswith('STRIPE_') or line.strip() == ''):
                    # Skip Stripe lines and empty line after section
                    if line.strip() == '':
                        in_stripe_section = False
                    continue
                else:
                    updated_lines.append(line)
            
            # Write back to .env file
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)
                
            print("Removed Stripe keys from .env file")
                
        except Exception as e:
            print(f"Error removing Stripe keys from .env: {e}")
    
    def _clear_python_cache(self):
        """Clear all Python cache files."""
        try:
            # Clear all __pycache__ directories
            for root, dirs, files in os.walk(self.modules_path):
                for dir_name in dirs:
                    if dir_name == '__pycache__':
                        cache_dir = os.path.join(root, dir_name)
                        shutil.rmtree(cache_dir)
                        print(f"Cleared cache: {cache_dir}")
        except Exception as e:
            print(f"Warning: Could not clear Python cache: {e}")
    
    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """Get a specific module instance."""
        return self.discovered_modules.get(module_name)
    
    def mark_module_uninstalled(self, module_name: str):
        """Mark a module as uninstalled."""
        uninstalled_modules = self._get_uninstalled_modules()
        uninstalled_modules.add(module_name)
        self._save_uninstalled_modules(uninstalled_modules)
    
    def mark_module_installed(self, module_name: str):
        """Mark a module as installed."""
        uninstalled_modules = self._get_uninstalled_modules()
        if module_name in uninstalled_modules:
            uninstalled_modules.remove(module_name)
            self._save_uninstalled_modules(uninstalled_modules)
    
    def _load_module(self, module_name, module_path):
        """Load a module dynamically."""
        try:
            # Import the module
            module_import_path = f"modules.{module_name}.module"
            module_module = importlib.import_module(module_import_path)
            
            # Find the module class (should inherit from BaseModule)
            module_class = None
            for name, obj in inspect.getmembers(module_module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseModule)
                    and obj != BaseModule
                    and not inspect.isabstract(obj)
                ):
                    module_class = obj
                    break
            
            if module_class:
                # Create instance with module name and path
                module_instance = module_class(module_name, module_path)
                return module_instance
            else:
                print(f"No valid module class found in {module_name}")
                return None
                
        except ImportError as e:
            print(f"Import error for {module_name}: {e}")
            return None
        except Exception as e:
            print(f"Error loading {module_name}: {e}")
            return None


# Create global module manager instance
module_manager = ModuleManager() 