# Module Distribution Guide

## Overview

This guide covers how to package, distribute, and upload modules as ZIP files. For module development, see the main [README.md](README.md).

## Quick Start

### Create a Module ZIP
```bash
# Create ZIP from installed module
python3 create_module_zip.py create <module_name> <output_name>

# Create improved version from existing ZIP
python3 create_module_zip.py improve-module <source_zip> <output_name>

# Example
python3 create_module_zip.py create my_payment_module my_payment_module_v1
```

### Upload a Module
1. Go to `/modules/` in your admin panel
2. Click "Upload Module" 
3. Drag and drop your ZIP file
4. The module will be automatically installed and registered

## ZIP File Structure

Your module ZIP must follow this structure:

```
module_name.zip
├── manifest.json          # Module metadata (required)
├── module.py             # Main module class (required)
├── __init__.py           # Python package init (required)
├── requirements.txt      # Python dependencies (optional)
├── templates/            # Django templates (optional)
│   └── module_name/
│       ├── payment_form.html
│       └── admin/
│           └── config.html
├── static/               # Static files (optional)
│   └── module_name/
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/           # Database migrations (optional)
├── forms.py             # Django forms (optional)
├── models.py            # Django models (optional)
├── views.py             # Django views (optional)
├── admin.py             # Django admin (optional)
├── urls.py              # URL patterns (optional)
└── README.md            # Module docs (optional)
```

## Required Files

### 1. manifest.json
```json
{
    "name": "payment_gateway",
    "version": "1.0.0",
    "description": "Payment gateway integration module",
    "author": "Your Name",
    "type": "payment",
    "dependencies": ["requests"],
    "python_version": ">=3.8",
    "django_version": ">=4.0",
    "install_requires": [
        "requests>=2.25.0"
    ],
    "settings": {
        "API_KEY": "",
        "SECRET_KEY": "",
        "WEBHOOK_SECRET": ""
    },
    "permissions": [
        "modules.view_module",
        "modules.change_module"
    ]
}
```

### 2. module.py
```python
from modules.base import PaymentModuleBase

class PaymentGatewayModule(PaymentModuleBase):
    name = "payment_gateway"
    version = "1.0.0"
    description = "Payment gateway integration module"
    author = "Your Name"
    type = "payment"
    
    def install(self):
        """Install the module."""
        # Database setup, settings configuration, etc.
        return True
    
    def uninstall(self):
        """Uninstall the module."""
        # Cleanup database, remove settings, etc.
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
default_app_config = 'modules.payment_gateway.apps.PaymentGatewayConfig'
```

## Creating ZIP Files

### Using the Script (Recommended)
```bash
# ✅ Always use the script for reliability
python3 create_module_zip.py create my_module my_module_v1

# ✅ Create improved versions from existing ZIPs
python3 create_module_zip.py improve-module existing_module new_version
```

### Manual Creation (Not Recommended)
```bash
# ❌ Avoid manual creation - prone to errors
cd modules/
zip -r my_module.zip my_module/ -x "*/__pycache__/*" "*/.*"
```

### Why Use the Script?
- ✅ **Reliable**: Always creates ZIPs in the correct location
- ✅ **Consistent**: Same structure every time  
- ✅ **Verifiable**: Shows what files are included
- ✅ **Proper Paths**: Uses Django settings for correct paths
- ✅ **Error Prevention**: Avoids common manual ZIP mistakes

## Upload Process

### Web Interface
1. Navigate to `/modules/` in admin
2. Click "Upload Module"
3. Select or drag your ZIP file
4. The system will:
   - Validate ZIP structure
   - Extract to modules directory
   - Load and register the module
   - Run the install() method
   - Enable the module

### Validation Rules
The system validates:
- ✅ Valid ZIP format
- ✅ Contains required files (manifest.json, module.py, __init__.py)
- ✅ module.py contains valid class inheriting from base
- ✅ Proper directory structure
- ✅ No conflicting module names

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

1. **Upload**: ZIP file uploaded and validated
2. **Extract**: Files extracted to modules directory  
3. **Validate**: Structure and manifest validated
4. **Install**: Module install() method called
5. **Register**: Module registered in system
6. **Enable**: Module enabled and ready for use

## Best Practices

### Version Naming
```bash
# ✅ Clear version names
payment_gateway_module_v2
my_module_beta_v1
shipping_calculator_final

# ❌ Unclear names  
module_new.zip
fixed_version.zip
```

### File Organization
- Keep templates in `templates/module_name/`
- Keep static files in `static/module_name/`
- Include all dependencies in requirements.txt
- Always test ZIP files before distribution

### Testing
```bash
# Verify ZIP is accessible
curl -I http://localhost:8000/downloads/your_module.zip

# Test module structure
unzip -l your_module.zip
```

## Troubleshooting

### Upload Failures
- **"No module.py file found"**: Check ZIP structure
- **"Invalid module class"**: Ensure class inherits from correct base
- **"Module already exists"**: System will overwrite existing
- **"Failed to load module"**: Check for syntax errors

### ZIP Creation Issues
- **File not in downloads**: Check script output and permissions
- **Browser can't download**: Clear cache or check file permissions  
- **ZIP corrupted**: Use the script instead of manual creation

### Module Not Working
1. Verify ZIP structure with `unzip -l module.zip`
2. Check module installation logs
3. Ensure all required files are included
4. Test with a known working version

## Security Considerations

- Only upload modules from trusted sources
- Review module code before installation in production
- Modules have full Django application access
- Consider sandboxing for third-party modules

## Support

- Check Django logs for detailed error messages
- Use the ZIP creation script for reliable packaging
- Test modules thoroughly before distribution
- Follow the standardized structure for compatibility 