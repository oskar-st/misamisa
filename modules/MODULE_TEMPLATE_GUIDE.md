# Module Creation Guide

## Quick Template for Payment Modules

### 1. Required Files Structure:
```
your_module/
├── manifest.json
├── module.py
├── views.py
├── models.py
├── __init__.py
├── templates/
│   └── your_module/
│       ├── payment_form.html
│       ├── payment_success.html
│       ├── payment_error.html
│       └── admin/
│           └── config.html
└── static/
    └── your_module/
        ├── css/
        └── js/
```

### 2. module.py Template:
```python
from modules.base import PaymentModuleBase
from django.urls import path
from . import views

class YourModule(PaymentModuleBase):  # Use PaymentModuleBase for payment modules
    name = "your_module_name"
    display_name = "Your Module Display Name"
    description = "Your module description"
    version = "1.0.0"
    author = "Your Name"
    category = "payment"
    
    def get_urls(self):
        return [
            path('your-payment/', views.payment_form, name='your_payment_form'),
            path('your-payment/process/', views.process_payment, name='your_payment_process'),
            path('your-payment/success/', views.payment_success, name='your_payment_success'),
            path('your-payment/error/', views.payment_error, name='your_payment_error'),
        ]
    
    def install(self):
        return True
    
    def uninstall(self):
        return True
    
    def get_payment_methods(self):
        return [
            {
                'id': 'your_payment_method',
                'name': 'Your Payment Method',
                'description': 'Description of your payment method',
                'icon': 'fas fa-icon-name',
                'form_template': 'your_module/payment_form.html',
                'success_template': 'your_module/payment_success.html',
                'error_template': 'your_module/payment_error.html',
            }
        ]
```

### 3. manifest.json Template:
```json
{
    "name": "your_module_name",
    "version": "1.0.0",
    "description": "Your module description",
    "author": "Your Name",
    "category": "payment",
    "type": "payment",
    "install_requires": [],
    "settings": {
        "setting_name": {"type": "string", "default": "default_value", "label": "Setting Label"}
    }
}
```

### 4. Key Points:
- **Class Name**: Use `PaymentModuleBase` for payment modules, `ShippingModuleBase` for shipping modules
- **Module Name**: Must be lowercase with underscores only (no spaces, hyphens, or special chars)
- **Template Paths**: Must match your module name in templates/your_module/
- **URL Names**: Must be unique across all modules

### 5. Common Issues:
- ❌ `"name": "Your Module Name"` (spaces not allowed)
- ❌ `class YourModule(BaseModule)` (use specific base class)
- ❌ Missing required template files
- ❌ Incorrect template paths

### 6. Testing:
1. Create your module files
2. Zip the entire module directory
3. Upload via admin panel
4. Check server logs for any errors

This template should work for most payment modules! 