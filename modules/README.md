# Module System Documentation

This module system provides a flexible, extensible architecture for Django applications, similar to PrestaShop's module system. It allows you to create reusable modules for various functionalities like design, shipping, payment, and more.

## Features

- **Modular Architecture**: Create self-contained modules with their own models, views, and templates
- **Hot Loading**: Modules can be installed/uninstalled without restarting the application
- **Dashboard Integration**: Modules can provide dashboard widgets and menu items
- **Admin Integration**: Automatic registration of module models with Django admin
- **Configuration Management**: Each module can have its own configuration interface
- **Permission System**: Built-in permission management for module features
- **API Support**: RESTful API endpoints for module management

## Quick Start

### 1. Load Modules

```bash
# Load all modules
python manage.py load_modules

# Load and install modules
python manage.py load_modules --install

# Load specific module
python manage.py load_modules --module design

# Load, install, and run migrations
python manage.py load_modules --install --migrate
```

### 2. Access Module Management

Visit `/modules/` in your browser to access the module management interface.

## Creating a New Module

### 1. Module Structure

Create a new directory in the `modules/` folder with the following structure:

```
modules/
└── your_module/
    ├── __init__.py
    ├── module.py          # Main module class
    ├── views.py           # Module views
    ├── admin_views.py     # Admin views
    ├── models.py          # Module models (optional)
    ├── templates/         # Module templates
    │   └── your_module/
    ├── static/            # Module static files
    │   └── your_module/
    └── config.json        # Module configuration (optional)
```

### 2. Module Class

Create your module class by inheriting from `ModuleBase`:

```python
# modules/your_module/module.py
from modules.base import ModuleBase
from django.db import models
from django.contrib.admin import ModelAdmin

class YourModule(ModuleBase):
    name = "Your Module"
    description = "Description of your module"
    version = "1.0.0"
    author = "Your Name"
    category = "general"  # design, shipping, payment, general
    icon = "fas fa-star"
    
    is_configurable = True
    requires_database = True
    
    def get_models(self):
        """Return list of module models."""
        return [YourModel]
    
    def get_admin_classes(self):
        """Return list of admin classes."""
        return [YourModelAdmin]
    
    def get_urls(self):
        """Return module URL patterns."""
        from . import views
        return [
            path('list/', views.your_list_view, name='your_list'),
            path('detail/<int:pk>/', views.your_detail_view, name='your_detail'),
        ]
    
    def get_dashboard_widgets(self):
        """Return dashboard widgets."""
        return [
            {
                'title': 'Your Widget',
                'content': self._get_widget_content(),
                'icon': 'fas fa-chart-bar',
                'color': 'primary',
                'size': 'small'
            }
        ]
    
    def get_menu_items(self):
        """Return menu items."""
        return [
            {
                'title': 'Your Menu',
                'url': '/module/your_module/list/',
                'icon': 'fas fa-list',
                'permission': 'your_module.view_yourmodel'
            }
        ]
    
    def install(self):
        """Install the module."""
        # Create initial data, etc.
        return True
    
    def uninstall(self):
        """Uninstall the module."""
        # Clean up data if needed
        return True
```

### 3. Models

Define your models in the module:

```python
# modules/your_module/models.py
from django.db import models

class YourModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

### 4. Views

Create views for your module:

```python
# modules/your_module/views.py
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from .models import YourModel

@login_required
def your_list_view(request: HttpRequest) -> HttpResponse:
    objects = YourModel.objects.all()
    context = {'objects': objects}
    return TemplateResponse(request, 'your_module/list.html', context)

@login_required
def your_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(YourModel, pk=pk)
    context = {'object': obj}
    return TemplateResponse(request, 'your_module/detail.html', context)
```

### 5. Templates

Create templates for your module:

```html
<!-- modules/your_module/templates/your_module/list.html -->
{% extends 'admin/base_site.html' %}

{% block content %}
<div id="content-main">
    <h1>Your Module List</h1>
    
    {% for obj in objects %}
    <div class="object-item">
        <h3>{{ obj.name }}</h3>
        <p>{{ obj.description }}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

## Module Categories

Modules are organized into categories:

- **Design**: Theme management, styling, UI components
- **Shipping**: Shipping methods, zones, calculations
- **Payment**: Payment gateways, transactions, processing
- **General**: Utility modules, tools, integrations

## Module Configuration

Modules can have configuration forms:

```python
def get_config_form(self):
    """Return configuration form template."""
    return 'your_module/config_form.html'

def save_config(self, data):
    """Save module configuration."""
    # Save configuration to database or file
    return True
```

## Dashboard Widgets

Modules can provide dashboard widgets:

```python
def get_dashboard_widgets(self):
    return [
        {
            'title': 'Widget Title',
            'content': self._get_widget_content(),
            'icon': 'fas fa-icon',
            'color': 'primary',  # primary, success, warning, danger, info
            'size': 'small'      # small, medium, large
        }
    ]
```

## Menu Integration

Modules can add menu items:

```python
def get_menu_items(self):
    return [
        {
            'title': 'Menu Item',
            'url': '/module/your_module/',
            'icon': 'fas fa-icon',
            'permission': 'your_module.view_yourmodel'
        }
    ]
```

## Permissions

Modules can define their own permissions:

```python
def get_permissions(self):
    return [
        'your_module.view_yourmodel',
        'your_module.add_yourmodel',
        'your_module.change_yourmodel',
        'your_module.delete_yourmodel',
    ]
```

## API Endpoints

The module system provides API endpoints:

- `GET /modules/api/` - List all modules
- `GET /modules/api/?module=module_name` - Get specific module info
- `POST /modules/api/` - Perform module operations (install, uninstall, activate, deactivate)

## Example Modules

### Design Module
- Theme management
- Color customization
- Font selection
- Layout options

### Shipping Module
- Shipping zones
- Shipping methods
- Cost calculation
- Delivery tracking

### Payment Module
- Payment gateways
- Transaction processing
- Fee calculation
- Payment analytics

## Best Practices

1. **Keep modules self-contained**: Each module should be independent
2. **Use meaningful names**: Module names should be descriptive
3. **Provide documentation**: Include README files for complex modules
4. **Handle errors gracefully**: Always handle exceptions in module methods
5. **Use migrations**: Create migrations for database changes
6. **Test modules**: Write tests for module functionality
7. **Version your modules**: Use semantic versioning
8. **Document dependencies**: List any external dependencies

## Troubleshooting

### Module not loading
- Check that the module directory exists in `modules/`
- Ensure `module.py` contains a class that inherits from `ModuleBase`
- Check for import errors in the module

### Models not appearing in admin
- Run `python manage.py load_modules` to register models
- Check that `get_models()` and `get_admin_classes()` return the correct lists
- Ensure models are properly defined

### URLs not working
- Check that `get_urls()` returns valid URL patterns
- Ensure the module is active and installed
- Check for URL conflicts with other modules

## Contributing

When creating modules for reuse:

1. Follow the established structure
2. Include comprehensive documentation
3. Add proper error handling
4. Include example usage
5. Test thoroughly
6. Version appropriately

## License

This module system is part of your Django application and follows the same license terms.

# Module Management System

## Complete Module Removal

The module system now includes a comprehensive module removal functionality that completely removes modules from the system.

### What Complete Removal Does

When you use the "Complete Remove" functionality, it will:

1. **Uninstall the module** - Calls the module's `uninstall()` method
2. **Delete all database records** - Removes all data from the module's models
3. **Remove module files** - Deletes the entire module directory from the filesystem
4. **Clean up registry** - Removes the module from the module registry
5. **Clear cached imports** - Removes any cached Python imports

### How to Use

#### Via Web Interface

1. Go to `/modules/` in your admin panel
2. Find the module you want to remove
3. Click the **"Complete Remove"** button (red button with warning icon)
4. Confirm the action in the warning dialog
5. The module will be completely removed from the system

#### Via API

```bash
# Complete removal via AJAX
curl -X POST /modules/complete-remove/module_name/ \
  -H "X-CSRFToken: your_csrf_token"
```

#### Via Django Shell

```python
from modules.manager import module_manager

# Completely remove a module
success = module_manager.completely_remove_module('module_name')
if success:
    print("Module completely removed")
else:
    print("Failed to remove module")
```

### Warning

⚠️ **This action is irreversible!** Once you complete the removal:

- All module files will be deleted
- All database records will be removed
- All configurations will be lost
- The module cannot be recovered without re-uploading

### Safety Features

- **Confirmation Dialog**: A detailed warning dialog appears before removal
- **Visual Distinction**: The complete remove button is styled differently to indicate danger
- **Admin Only**: Only admin users can perform complete removal
- **Error Handling**: Comprehensive error handling prevents partial removals

### Module States

- **Installed**: Module is installed but can be uninstalled (keeps files)
- **Uninstalled**: Module is not active but files remain
- **Completely Removed**: Module and all its files are gone from the system

### Recovery

If you accidentally remove a module, you can:

1. Re-upload the module ZIP file via the upload interface
2. Re-install the module
3. Re-configure the module settings

However, any data that was in the database will be permanently lost. 