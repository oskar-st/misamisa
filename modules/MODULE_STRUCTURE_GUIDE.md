# Standardized Module ZIP Structure Guide

## Overview
This guide defines the standardized structure for module ZIP files to ensure reliable upload, installation, uninstallation, and enabling processes.

## ZIP File Structure
```
module_name.zip
├── manifest.json          # Module metadata and configuration
├── module.py             # Main module class
├── __init__.py           # Python package initialization
├── requirements.txt      # Python dependencies (optional)
├── templates/            # Django templates
│   └── module_name/
│       ├── payment_form.html
│       └── admin/
│           └── config.html
├── static/               # Static files (CSS, JS, images)
│   └── module_name/
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/           # Database migrations (optional)
│   └── __init__.py
├── forms.py             # Django forms (optional)
├── models.py            # Django models (optional)
├── views.py             # Django views (optional)
├── admin.py             # Django admin (optional)
├── urls.py              # URL patterns (optional)
└── README.md            # Module documentation (optional)
```

## Required Files

### 1. manifest.json
```json
{
    "name": "stripe_payment",
    "version": "1.0.0",
    "description": "Stripe payment gateway integration",
    "author": "Your Name",
    "type": "payment",
    "dependencies": ["stripe"],
    "python_version": ">=3.8",
    "django_version": ">=4.0",
    "install_requires": [
        "stripe>=5.0.0"
    ],
    "settings": {
        "STRIPE_PUBLIC_KEY": "",
        "STRIPE_SECRET_KEY": "",
        "STRIPE_WEBHOOK_SECRET": ""
    },
    "permissions": [
        "modules.view_module",
        "modules.change_module"
    ],
    "hooks": {
        "post_install": "setup_stripe_webhooks",
        "pre_uninstall": "cleanup_stripe_webhooks"
    }
}
```

### 2. module.py
```python
from modules.base import PaymentModuleBase

class StripePaymentModule(PaymentModuleBase):
    name = "stripe_payment"
    version = "1.0.0"
    description = "Stripe payment gateway integration"
    author = "Your Name"
    type = "payment"
    
    def install(self):
        """Install the module."""
        # Database setup
        # Settings configuration
        # Webhook setup
        return True
    
    def uninstall(self):
        """Uninstall the module."""
        # Cleanup database
        # Remove settings
        # Remove webhooks
        return True
    
    def enable(self):
        """Enable the module."""
        return True
    
    def disable(self):
        """Disable the module."""
        return True
```

### 3. __init__.py
```python
# Module package initialization
default_app_config = 'modules.stripe_payment.apps.StripePaymentConfig'
```

## Module Types

### Payment Modules
- Must inherit from `PaymentModuleBase`
- Must implement payment processing methods
- Must provide payment form templates

### Shipping Modules
- Must inherit from `ShippingModuleBase`
- Must implement shipping calculation methods
- Must provide shipping configuration templates

### Design Modules
- Must inherit from `DesignModuleBase`
- Must implement theme customization methods
- Must provide design configuration templates

## Installation Process

1. **Upload**: ZIP file is uploaded and validated
2. **Extract**: ZIP is extracted to temporary directory
3. **Validate**: Structure and manifest are validated
4. **Install**: Module is installed to modules directory
5. **Load**: Module is loaded into the system
6. **Configure**: Module settings are configured
7. **Enable**: Module is enabled and ready for use

## Uninstallation Process

1. **Disable**: Module is disabled
2. **Uninstall**: Module is uninstalled from system
3. **Cleanup**: Database records are cleaned up
4. **Remove**: Module files are removed
5. **Cache**: Python cache is cleared

## Best Practices

1. **Version Control**: Always include version in manifest
2. **Dependencies**: List all Python dependencies
3. **Settings**: Define required settings in manifest
4. **Permissions**: Specify required permissions
5. **Documentation**: Include README.md with usage instructions
6. **Testing**: Test installation/uninstallation thoroughly
7. **Backup**: Always backup before installing modules

## Validation Rules

1. **Required Files**: manifest.json, module.py, __init__.py
2. **Manifest**: Valid JSON with required fields
3. **Module Class**: Must inherit from appropriate base class
4. **Templates**: Must be in templates/module_name/ directory
5. **Static Files**: Must be in static/module_name/ directory
6. **No Conflicts**: Module name must not conflict with existing modules

## Error Handling

1. **Upload Errors**: Invalid ZIP, missing files, corrupted archive
2. **Validation Errors**: Invalid manifest, missing required files
3. **Installation Errors**: Database errors, permission issues
4. **Loading Errors**: Import errors, class definition issues
5. **Configuration Errors**: Invalid settings, missing dependencies

## Security Considerations

1. **File Validation**: Validate all uploaded files
2. **Code Review**: Review module code before installation
3. **Permissions**: Limit module permissions to minimum required
4. **Isolation**: Modules should not access system files outside their scope
5. **Updates**: Regular security updates for modules 