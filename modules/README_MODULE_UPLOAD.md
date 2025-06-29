# Module Upload System

This system allows you to upload modules via ZIP files, similar to PrestaShop's module upload functionality.

## Module ZIP File Structure

Your module ZIP file should have the following structure:

```
my_module.zip
└── my_module/
    ├── module.py          # Required: Main module file
    ├── __init__.py        # Optional: Package initialization
    ├── views.py           # Optional: Module views
    ├── admin_views.py     # Optional: Admin views
    ├── templates/         # Optional: Template files
    │   └── modules/
    │       └── my_module/
    │           └── index.html
    ├── static/            # Optional: Static files
    │   └── modules/
    │       └── my_module/
    │           ├── css/
    │           └── js/
    └── migrations/        # Optional: Database migrations
        └── 0001_initial.py
```

## Module.py Requirements

Your `module.py` file must contain a class that inherits from `ModuleBase`:

```python
from modules.base import ModuleBase

class MyModule(ModuleBase):
    name = "My Module"
    description = "Description of my module"
    version = "1.0.0"
    author = "Your Name"
    category = "general"
    icon = "fas fa-star"
    
    # ... rest of your module implementation
```

## Creating a Module ZIP File

1. **Create your module directory structure** as shown above
2. **Zip the module directory** (not the parent folder)
3. **Upload via the web interface** at `/modules/upload/`

## Example: Creating a Test Module

Here's how to create a simple test module:

1. Create a directory called `test_module`
2. Create `test_module/module.py`:

```python
from modules.base import ModuleBase

class TestModule(ModuleBase):
    name = "Test Module"
    description = "A simple test module"
    version = "1.0.0"
    author = "Test Author"
    category = "general"
    icon = "fas fa-test"
    
    is_configurable = False
    requires_database = False
    
    def get_urls(self):
        return []
    
    def get_admin_urls(self):
        return []
    
    def get_templates(self):
        return []
    
    def get_static_files(self):
        return []
    
    def install(self):
        return True
    
    def uninstall(self):
        return True
```

3. Create `test_module/__init__.py` (empty file)
4. Zip the `test_module` directory (not the parent folder)
5. Upload the ZIP file via the web interface

## Upload Process

1. Go to `/modules/` in your admin panel
2. Click "Upload Module"
3. Drag and drop your ZIP file or click to browse
4. The system will:
   - Validate the ZIP file structure
   - Extract the module
   - Load and register the module
   - Install the module automatically

## Validation Rules

The upload system validates:

- ✅ ZIP file format
- ✅ Contains `module.py` file
- ✅ `module.py` contains a class inheriting from `ModuleBase`
- ✅ Proper directory structure
- ✅ No conflicting module names

## Error Handling

Common errors and solutions:

- **"No module.py file found"**: Ensure your ZIP contains a `module.py` file
- **"Invalid module structure"**: Check that your class inherits from `ModuleBase`
- **"Module already exists"**: The system will overwrite existing modules
- **"Failed to load module"**: Check for syntax errors in your `module.py`

## Security Considerations

- Only upload modules from trusted sources
- The system validates module structure but doesn't scan for malicious code
- Consider reviewing module code before installation
- Modules have access to your Django application

## Troubleshooting

If upload fails:

1. Check the ZIP file structure
2. Verify `module.py` syntax
3. Ensure the module class inherits from `ModuleBase`
4. Check file permissions on the server
5. Review Django logs for detailed error messages 