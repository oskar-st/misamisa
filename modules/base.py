"""
Base module classes and utilities for the modular system.
"""
import os
import json
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.template.loader import get_template
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path, include
from django.contrib import admin
from django.contrib.admin import AdminSite

class ModuleManifest:
    """Standardized module manifest for validation and metadata"""
    
    def __init__(self, manifest_data: Dict[str, Any]):
        self.name = manifest_data.get('name', '')
        self.version = manifest_data.get('version', '1.0.0')
        self.description = manifest_data.get('description', '')
        self.author = manifest_data.get('author', '')
        self.type = manifest_data.get('type', 'general')  # payment, shipping, design, etc.
        self.dependencies = manifest_data.get('dependencies', [])
        self.requires_python = manifest_data.get('requires_python', '>=3.8')
        self.install_requires = manifest_data.get('install_requires', [])
        self.templates = manifest_data.get('templates', [])
        self.static_files = manifest_data.get('static_files', [])
        self.admin_config = manifest_data.get('admin_config', False)
        self.migrations = manifest_data.get('migrations', False)
        self.urls = manifest_data.get('urls', {})
        self.settings = manifest_data.get('settings', {})
        
    @classmethod
    def from_file(cls, manifest_path: str) -> 'ModuleManifest':
        """Load manifest from JSON file"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid manifest file: {e}")
    
    def validate(self) -> List[str]:
        """Validate manifest data and return list of errors"""
        errors = []
        
        if not self.name:
            errors.append("Module name is required")
        
        if not self.version:
            errors.append("Module version is required")
            
        if not self.description:
            errors.append("Module description is required")
            
        if not self.type:
            errors.append("Module type is required")
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest back to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'type': self.type,
            'dependencies': self.dependencies,
            'requires_python': self.requires_python,
            'install_requires': self.install_requires,
            'templates': self.templates,
            'static_files': self.static_files,
            'admin_config': self.admin_config,
            'migrations': self.migrations,
            'urls': self.urls,
            'settings': self.settings,
        }


class BaseModule(ABC):
    """Base class for all modules with standardized structure"""
    
    def __init__(self, module_name: str, module_path: str):
        self.module_name = module_name
        self.module_path = module_path
        self.manifest = self._load_manifest()
        self.is_installed = False
        self.is_enabled = False
        
    def _load_manifest(self) -> Optional[ModuleManifest]:
        """Load module manifest from manifest.json"""
        manifest_path = os.path.join(self.module_path, 'manifest.json')
        if os.path.exists(manifest_path):
            try:
                return ModuleManifest.from_file(manifest_path)
            except ValueError:
                return None
        return None
    
    @property
    def has_manifest(self) -> bool:
        """Check if module has a valid manifest"""
        return self.manifest is not None and not self.manifest.validate()
    
    @property
    def module_type(self) -> str:
        """Get module type from manifest"""
        return self.manifest.type if self.manifest else 'general'
    
    @property
    def module_version(self) -> str:
        """Get module version from manifest"""
        return self.manifest.version if self.manifest else '1.0.0'
    
    @property
    def module_description(self) -> str:
        """Get module description from manifest"""
        return self.manifest.description if self.manifest else ''
    
    @abstractmethod
    def install(self) -> bool:
        """Install the module - create database tables, etc."""
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall the module - remove database tables, etc."""
        pass
    
    @abstractmethod
    def enable(self) -> bool:
        """Enable the module"""
        pass
    
    @abstractmethod
    def disable(self) -> bool:
        """Disable the module"""
        pass
    
    def get_urls(self) -> List:
        """Get module URL patterns"""
        return []
    
    def get_admin_config(self) -> Optional[str]:
        """Get admin configuration template path"""
        if self.manifest and self.manifest.admin_config:
            admin_path = os.path.join(self.module_path, 'admin', 'config.html')
            if os.path.exists(admin_path):
                return f"{self.module_name}/admin/config.html"
        return None
    
    def get_templates(self) -> List[str]:
        """Get list of template paths"""
        if self.manifest:
            return [f"{self.module_name}/{template}" for template in self.manifest.templates]
        return []
    
    def get_static_files(self) -> List[str]:
        """Get list of static file paths"""
        if self.manifest:
            return [f"{self.module_name}/{static}" for static in self.manifest.static_files]
        return []
    
    def validate_structure(self) -> List[str]:
        """Validate module directory structure"""
        errors = []
        
        # Check required files
        required_files = ['module.py', '__init__.py']
        for file in required_files:
            if not os.path.exists(os.path.join(self.module_path, file)):
                errors.append(f"Missing required file: {file}")
        
        # Check manifest
        if not self.has_manifest:
            errors.append("Invalid or missing manifest.json")
        
        # Check module.py has required class
        module_py_path = os.path.join(self.module_path, 'module.py')
        if os.path.exists(module_py_path):
            try:
                with open(module_py_path, 'r') as f:
                    content = f.read()
                    if 'class' not in content or 'BaseModule' not in content:
                        errors.append("module.py must contain a class inheriting from BaseModule")
            except Exception:
                errors.append("Cannot read module.py file")
        
        return errors


class PaymentModuleBase(BaseModule):
    """Base class for payment modules"""
    
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
        if self.manifest:
            self.manifest.type = 'payment'
    
    @abstractmethod
    def get_payment_form(self) -> Form:
        """Return the payment form class"""
        pass
    
    @abstractmethod
    def get_payment_template(self) -> str:
        """Return the payment form template path"""
        pass
    
    @abstractmethod
    def process_payment(self, request: HttpRequest, form_data: Dict) -> Dict[str, Any]:
        """Process payment and return result"""
        pass
    
    @abstractmethod
    def validate_payment_data(self, form_data: Dict) -> List[str]:
        """Validate payment form data"""
        pass
        
    def get_settings(self) -> Dict[str, Any]:
        """Get module settings from manifest or return defaults"""
        if self.manifest and self.manifest.settings:
            return self.manifest.settings
        return {}
    
    def get_admin_config_template(self) -> str:
        """Get admin configuration template for payment modules"""
        return f"{self.module_name}/admin/config.html"


class ShippingModuleBase(BaseModule):
    """Base class for shipping modules"""
    
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
        if self.manifest:
            self.manifest.type = 'shipping'
    
    @abstractmethod
    def calculate_shipping(self, cart_items: List, destination: Dict) -> Dict[str, Any]:
        """Calculate shipping cost"""
        pass
    
    @abstractmethod
    def get_shipping_methods(self) -> List[Dict[str, Any]]:
        """Get available shipping methods"""
        pass


class DesignModuleBase(BaseModule):
    """Base class for design/theme modules"""
    
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
        if self.manifest:
            self.manifest.type = 'design'
    
    @abstractmethod
    def get_theme_config(self) -> Dict[str, Any]:
        """Get theme configuration"""
        pass
    
    @abstractmethod
    def apply_theme(self, template_name: str, context: Dict) -> str:
        """Apply theme to template"""
        pass 