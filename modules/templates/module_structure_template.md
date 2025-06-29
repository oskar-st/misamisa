# Standard Module Structure Template

## Directory Structure
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
    requirements.txt           # Python dependencies (optional)
    README.md                  # Module documentation (optional)
```

## manifest.json Template
```json
{
  "name": "My Module",
  "version": "1.0.0",
  "description": "A description of what this module does",
  "author": "Your Name",
  "type": "payment",
  "dependencies": [],
  "requires_python": ">=3.8",
  "install_requires": [
    "some-package>=1.0.0"
  ],
  "templates": [
    "payment_form.html",
    "admin/config.html"
  ],
  "static_files": [
    "css/style.css",
    "js/script.js"
  ],
  "admin_config": true,
  "migrations": true,
  "urls": {
    "public": [
      "path('my-module/', views.my_view, name='my_view')"
    ],
    "admin": [
      "path('my-module/', admin_views.my_admin_view, name='my_admin_view')"
    ]
  },
  "settings": {
    "MY_MODULE_ENABLED": true,
    "MY_MODULE_API_KEY": ""
  }
}
```

## module.py Template
```python
from modules.base import PaymentModuleBase
from django.forms import Form
from django.http import HttpRequest
from typing import Dict, List, Any

class MyModule(PaymentModuleBase):
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
    
    def install(self) -> bool:
        """Install the module"""
        try:
            # Create database tables, etc.
            return True
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall the module"""
        try:
            # Remove database tables, etc.
            return True
        except Exception as e:
            print(f"Uninstallation failed: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the module"""
        self.is_enabled = True
        return True
    
    def disable(self) -> bool:
        """Disable the module"""
        self.is_enabled = False
        return True
    
    def get_payment_form(self) -> Form:
        """Return the payment form class"""
        from .forms import MyPaymentForm
        return MyPaymentForm
    
    def get_payment_template(self) -> str:
        """Return the payment form template path"""
        return f"{self.module_name}/payment_form.html"
    
    def process_payment(self, request: HttpRequest, form_data: Dict) -> Dict[str, Any]:
        """Process payment and return result"""
        # Implement payment processing logic
        return {
            'success': True,
            'transaction_id': 'txn_123',
            'message': 'Payment processed successfully'
        }
    
    def validate_payment_data(self, form_data: Dict) -> List[str]:
        """Validate payment form data"""
        errors = []
        # Implement validation logic
        return errors
``` 