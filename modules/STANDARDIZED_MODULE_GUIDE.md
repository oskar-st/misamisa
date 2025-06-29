# Standardized Module System Guide

## Overview

This guide explains the new standardized module system that makes it easy to create, install, and manage modules for the e-commerce platform.

## Module Structure

Every module must follow this standardized structure:

```
modules/
  my_module/
    __init__.py                 # Module initialization
    module.py                   # Main module class (inherits from BaseModule)
    manifest.json              # Module metadata and configuration
    forms.py                   # Django forms (optional)
    views.py                   # Django views (optional)
    models.py                  # Django models (optional)
    admin.py                   # Django admin (optional)
    admin_views.py             # Admin views (optional)
    admin/
      config.html              # Admin configuration template (optional)
    templates/
      my_module/
        payment_form.html      # Payment form template (for payment modules)
        other_templates.html   # Other templates
    static/
      my_module/
        css/
        js/
        images/
    migrations/                # Django migrations (optional)
```

## Required Files

### 1. `__init__.py`
```python
# Empty file to make the directory a Python package
```

### 2. `manifest.json`
```json
{
  "name": "My Module",
  "version": "1.0.0",
  "description": "Description of what this module does",
  "author": "Your Name",
  "type": "payment",
  "dependencies": [],
  "requires_python": ">=3.8",
  "install_requires": [
    "package_name>=1.0.0"
  ],
  "templates": [
    "payment_form.html"
  ],
  "static_files": [],
  "admin_config": true,
  "migrations": true,
  "urls": {
    "public": [
      "path('webhook/', views.webhook, name='webhook')"
    ],
    "admin": [
      "path('config/', admin_views.config, name='config')"
    ]
  },
  "settings": {
    "MODULE_ENABLED": true,
    "API_KEY": "",
    "SECRET_KEY": ""
  }
}
```

### 3. `module.py`
```python
from modules.base import PaymentModuleBase
from django.forms import Form
from django.http import HttpRequest
from typing import Dict, Any, List

class MyPaymentForm(Form):
    """Payment form for this module."""
    # Define your form fields here
    pass

class MyModule(PaymentModuleBase):
    """My payment module implementation."""
    
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
    
    def install(self) -> bool:
        """Install the module."""
        try:
            # Create database tables, etc.
            return True
        except Exception as e:
            print(f"Error installing module: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall the module."""
        try:
            # Remove database tables, etc.
            return True
        except Exception as e:
            print(f"Error uninstalling module: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the module."""
        self.is_enabled = True
        return True
    
    def disable(self) -> bool:
        """Disable the module."""
        self.is_enabled = False
        return True
    
    def get_payment_form(self) -> Form:
        """Return the payment form class."""
        return MyPaymentForm
    
    def get_payment_template(self) -> str:
        """Return the payment form template path."""
        return f"{self.module_name}/payment_form.html"
    
    def process_payment(self, request: HttpRequest, form_data: Dict) -> Dict[str, Any]:
        """Process payment and return result."""
        # Implement payment processing logic
        return {
            'success': True,
            'transaction_id': 'TXN-123',
            'message': 'Payment processed successfully',
            'status': 'completed'
        }
    
    def validate_payment_data(self, form_data: Dict) -> List[str]:
        """Validate payment form data."""
        errors = []
        # Add validation logic
        return errors
    
    def get_admin_config_template(self) -> str:
        """Get admin configuration template."""
        return f"{self.module_name}/admin/config.html"
```

## Module Types

### Payment Modules
- Inherit from `PaymentModuleBase`
- Must implement payment processing methods
- Used in checkout process

### Shipping Modules
- Inherit from `ShippingModuleBase`
- Must implement shipping calculation methods
- Used for shipping cost calculation

### Design Modules
- Inherit from `DesignModuleBase`
- Must implement theme application methods
- Used for customizing site appearance

## Creating a Module ZIP

1. Create your module following the structure above
2. Create a ZIP file containing the module directory:

```bash
cd modules/
zip -r my_module.zip my_module/ -x "*/__pycache__/*" "*/.*" "*/venv/*"
```

3. Upload the ZIP through the admin interface

## Module Installation Process

1. **Upload**: ZIP file is uploaded and validated
2. **Extract**: Module files are extracted to `modules/` directory
3. **Validate**: Module structure and manifest are validated
4. **Install**: Module's `install()` method is called
5. **Register**: Module is registered in the system
6. **Enable**: Module is enabled and ready to use

## Module Management

### Admin Interface
- Go to `/modules/` to see all modules
- Install/uninstall modules
- Enable/disable modules
- Configure module settings
- View module details

### Programmatic Access
```python
from modules.manager import module_manager

# Get all payment modules
payment_modules = module_manager.get_payment_modules()

# Get a specific module
module = module_manager.get_module('stripe')

# Install a module
module_manager.install_module('stripe')

# Uninstall a module
module_manager.uninstall_module('stripe')
```

## Template Integration

### Payment Form Templates
Payment modules should provide a `payment_form.html` template:

```html
<div class="payment-form">
    <h3>{{ module_name|title }} Payment</h3>
    
    <form method="post" id="payment-form">
        {% csrf_token %}
        {{ form.as_p }}
        
        <button type="submit" class="btn btn-primary">
            Pay with {{ module_name|title }}
        </button>
    </form>
</div>
```

### Admin Configuration Templates
Modules can provide admin configuration templates:

```html
{% extends 'admin/base_site.html' %}

{% block content %}
<div class="module-config">
    <h1>{{ module_name|title }} Configuration</h1>
    
    <form method="post">
        {% csrf_token %}
        <!-- Configuration form fields -->
        <button type="submit">Save Configuration</button>
    </form>
</div>
{% endblock %}
```

## Best Practices

1. **Follow the Structure**: Always follow the standardized directory structure
2. **Use Manifest**: Always include a complete `manifest.json`
3. **Handle Errors**: Implement proper error handling in all methods
4. **Validate Input**: Always validate user input and form data
5. **Document**: Include clear documentation for your module
6. **Test**: Test your module thoroughly before distribution
7. **Dependencies**: List all required dependencies in `manifest.json`
8. **Security**: Follow security best practices for payment processing

## Example: Complete Payment Module

See the `stripe` module in the `modules/stripe/` directory for a complete example of a payment module implementation.

## Troubleshooting

### Common Issues

1. **Template Not Found**: Ensure templates are in the correct directory structure
2. **Import Errors**: Check that all dependencies are installed
3. **Installation Fails**: Verify the module structure and manifest.json
4. **Module Not Loading**: Check that the module class inherits from the correct base class

### Debug Mode

Enable debug mode to see detailed error messages:

```python
# In your module's install method
import traceback
try:
    # Installation code
    pass
except Exception as e:
    print(f"Installation error: {e}")
    print(traceback.format_exc())
    return False
```

## Support

For questions or issues with the module system, check the logs and ensure your module follows the standardized structure outlined in this guide. 