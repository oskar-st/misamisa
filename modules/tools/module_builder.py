#!/usr/bin/env python3
"""
Module Builder Tool

This tool helps create properly structured module ZIP files
according to the standardized module structure.
"""

import os
import json
import zipfile
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class ModuleBuilder:
    """Tool for building standardized module ZIP files."""
    
    def __init__(self, module_name: str, module_type: str = "general"):
        self.module_name = module_name
        self.module_type = module_type
        self.module_dir = Path(f"build/{module_name}")
        self.manifest = self._create_default_manifest()
    
    def _create_default_manifest(self) -> Dict:
        """Create default manifest.json content."""
        return {
            "name": self.module_name,
            "version": "1.0.0",
            "description": f"{self.module_name} module",
            "author": "Module Author",
            "type": self.module_type,
            "dependencies": [],
            "python_version": ">=3.8",
            "django_version": ">=4.0",
            "install_requires": [],
            "settings": {},
            "permissions": [
                "modules.view_module",
                "modules.change_module"
            ],
            "hooks": {}
        }
    
    def create_directory_structure(self):
        """Create the standard module directory structure."""
        # Create main directories
        directories = [
            "",
            "templates",
            f"templates/{self.module_name}",
            f"templates/{self.module_name}/admin",
            "static",
            f"static/{self.module_name}",
            f"static/{self.module_name}/css",
            f"static/{self.module_name}/js",
            f"static/{self.module_name}/images",
            "migrations",
        ]
        
        for directory in directories:
            dir_path = self.module_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")
    
    def create_manifest(self, **kwargs):
        """Create manifest.json file."""
        # Update manifest with provided values
        for key, value in kwargs.items():
            if key in self.manifest:
                self.manifest[key] = value
        
        manifest_path = self.module_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=4)
        print(f"Created manifest.json: {manifest_path}")
    
    def create_module_py(self, base_class: str = "BaseModule"):
        """Create module.py file."""
        module_content = f'''"""
{self.module_name} module
"""

from modules.base import {base_class}


class {self.module_name.title().replace('_', '')}Module({base_class}):
    """{self.module_name} module implementation."""
    
    name = "{self.module_name}"
    version = "{self.manifest['version']}"
    description = "{self.manifest['description']}"
    author = "{self.manifest['author']}"
    type = "{self.manifest['type']}"
    
    def install(self):
        """Install the module."""
        try:
            # Add your installation logic here
            # - Database setup
            # - Settings configuration
            # - File copying
            return True
        except Exception as e:
            print(f"Installation error: {{e}}")
            return False
    
    def uninstall(self):
        """Uninstall the module."""
        try:
            # Add your uninstallation logic here
            # - Database cleanup
            # - Settings removal
            # - File cleanup
            return True
        except Exception as e:
            print(f"Uninstallation error: {{e}}")
            return False
    
    def enable(self):
        """Enable the module."""
        try:
            # Add your enable logic here
            return True
        except Exception as e:
            print(f"Enable error: {{e}}")
            return False
    
    def disable(self):
        """Disable the module."""
        try:
            # Add your disable logic here
            return True
        except Exception as e:
            print(f"Disable error: {{e}}")
            return False
'''
        
        module_path = self.module_dir / "module.py"
        with open(module_path, 'w') as f:
            f.write(module_content)
        print(f"Created module.py: {module_path}")
    
    def create_init_py(self):
        """Create __init__.py file."""
        init_content = f'''"""
{self.module_name} module package
"""

# Module package initialization
default_app_config = 'modules.{self.module_name}.apps.{self.module_name.title().replace("_", "")}Config'
'''
        
        init_path = self.module_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write(init_content)
        print(f"Created __init__.py: {init_path}")
    
    def create_requirements_txt(self, requirements: List[str] = None):
        """Create requirements.txt file."""
        if not requirements:
            requirements = []
        
        requirements_path = self.module_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            for req in requirements:
                f.write(f"{req}\n")
        print(f"Created requirements.txt: {requirements_path}")
    
    def create_readme_md(self):
        """Create README.md file."""
        readme_content = f'''# {self.module_name.title().replace('_', ' ')}

{self.manifest['description']}

## Installation

1. Upload the module ZIP file through the admin interface
2. The module will be automatically installed and enabled
3. Configure the module settings in the admin panel

## Configuration

This module requires the following settings:

{self._format_settings()}

## Usage

Describe how to use this module here.

## Dependencies

{self._format_dependencies()}

## Author

{self.manifest['author']}

## Version

{self.manifest['version']}
'''
        
        readme_path = self.module_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"Created README.md: {readme_path}")
    
    def _format_settings(self) -> str:
        """Format settings for README."""
        if not self.manifest['settings']:
            return "No additional settings required."
        
        settings_text = ""
        for key, value in self.manifest['settings'].items():
            settings_text += f"- `{key}`: {value}\n"
        return settings_text
    
    def _format_dependencies(self) -> str:
        """Format dependencies for README."""
        if not self.manifest['install_requires']:
            return "No additional dependencies required."
        
        deps_text = ""
        for dep in self.manifest['install_requires']:
            deps_text += f"- {dep}\n"
        return deps_text
    
    def create_template_files(self):
        """Create basic template files."""
        # Create payment form template for payment modules
        if self.module_type == "payment":
            payment_form = f'''<!-- {self.module_name} Payment Form -->
<div class="payment-form {self.module_name}-payment">
    <h3>{{ module.display_name }}</h3>
    <p>{{ module.description }}</p>
    
    <form method="post" id="{self.module_name}-form">
        {% csrf_token %}
        <div class="form-group">
            <label for="card_number">Card Number</label>
            <input type="text" id="card_number" name="card_number" class="form-control" required>
        </div>
        
        <div class="form-row">
            <div class="form-group col-md-6">
                <label for="expiry">Expiry Date</label>
                <input type="text" id="expiry" name="expiry" class="form-control" placeholder="MM/YY" required>
            </div>
            <div class="form-group col-md-6">
                <label for="cvv">CVV</label>
                <input type="text" id="cvv" name="cvv" class="form-control" required>
            </div>
        </div>
        
        <button type="submit" class="btn btn-primary">Pay {{ order.total_amount }}</button>
    </form>
</div>
'''
            
            template_path = self.module_dir / f"templates/{self.module_name}/payment_form.html"
            with open(template_path, 'w') as f:
                f.write(payment_form)
            print(f"Created payment form template: {template_path}")
        
        # Create admin config template
        admin_config = f'''<!-- {self.module_name} Admin Configuration -->
<div class="module-config {self.module_name}-config">
    <h3>{{ module.display_name }} Configuration</h3>
    
    <form method="post" class="config-form">
        {% csrf_token %}
        
        {% for field in config_form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}">{{ field.label }}</label>
            {{ field }}
            {% if field.help_text %}
            <small class="form-text text-muted">{{ field.help_text }}</small>
            {% endif %}
            {% if field.errors %}
            <div class="alert alert-danger">
                {{ field.errors }}
            </div>
            {% endif %}
        </div>
        {% endfor %}
        
        <button type="submit" class="btn btn-primary">Save Configuration</button>
    </form>
</div>
'''
        
        admin_template_path = self.module_dir / f"templates/{self.module_name}/admin/config.html"
        with open(admin_template_path, 'w') as f:
            f.write(admin_config)
        print(f"Created admin config template: {admin_template_path}")
    
    def create_static_files(self):
        """Create basic static files."""
        # Create CSS file
        css_content = f'''/* {self.module_name} Styles */
.{self.module_name}-payment {{
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 20px;
}}

.{self.module_name}-payment h3 {{
    color: #333;
    margin-bottom: 15px;
}}

.{self.module_name}-payment .form-group {{
    margin-bottom: 15px;
}}

.{self.module_name}-payment .form-control {{
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}}

.{self.module_name}-payment .btn {{
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}}

.{self.module_name}-payment .btn:hover {{
    background-color: #0056b3;
}}
'''
        
        css_path = self.module_dir / f"static/{self.module_name}/css/style.css"
        with open(css_path, 'w') as f:
            f.write(css_content)
        print(f"Created CSS file: {css_path}")
        
        # Create JS file
        js_content = f'''// {self.module_name} JavaScript
(function() {{
    'use strict';
    
    // Initialize {self.module_name} module
    function init{self.module_name.replace('_', '').title()}() {{
        console.log('{self.module_name} module initialized');
        
        // Add your JavaScript functionality here
        const form = document.getElementById('{self.module_name}-form');
        if (form) {{
            form.addEventListener('submit', function(e) {{
                // Handle form submission
                console.log('{self.module_name} form submitted');
            }});
        }}
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', init{self.module_name.replace('_', '').title()});
    }} else {{
        init{self.module_name.replace('_', '').title()}();
    }}
}})();
'''
        
        js_path = self.module_dir / f"static/{self.module_name}/js/script.js"
        with open(js_path, 'w') as f:
            f.write(js_content)
        print(f"Created JavaScript file: {js_path}")
    
    def create_migrations_init(self):
        """Create migrations __init__.py file."""
        migrations_init_path = self.module_dir / "migrations/__init__.py"
        with open(migrations_init_path, 'w') as f:
            f.write("# Django migrations package\n")
        print(f"Created migrations __init__.py: {migrations_init_path}")
    
    def build_zip(self, output_dir: str = "dist"):
        """Build the module ZIP file."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create ZIP file
        zip_path = output_path / f"{self.module_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.module_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(self.module_dir)
                    zipf.write(file_path, arc_name)
        
        print(f"Created module ZIP: {zip_path}")
        return zip_path
    
    def cleanup(self):
        """Clean up build directory."""
        if self.module_dir.exists():
            shutil.rmtree(self.module_dir)
            print(f"Cleaned up build directory: {self.module_dir}")


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Build standardized module ZIP files')
    parser.add_argument('module_name', help='Name of the module')
    parser.add_argument('--type', default='general', choices=['payment', 'shipping', 'design', 'general'],
                       help='Type of module')
    parser.add_argument('--description', help='Module description')
    parser.add_argument('--author', help='Module author')
    parser.add_argument('--version', default='1.0.0', help='Module version')
    parser.add_argument('--dependencies', nargs='*', help='Python dependencies')
    parser.add_argument('--keep-build', action='store_true', help='Keep build directory after creating ZIP')
    parser.add_argument('--output-dir', default='dist', help='Output directory for ZIP file')
    
    args = parser.parse_args()
    
    # Create module builder
    builder = ModuleBuilder(args.module_name, args.type)
    
    # Create directory structure
    builder.create_directory_structure()
    
    # Create files
    builder.create_manifest(
        description=args.description or f"{args.module_name} module",
        author=args.author or "Module Author",
        version=args.version,
        install_requires=args.dependencies or []
    )
    
    # Determine base class based on module type
    base_class_map = {
        'payment': 'PaymentModuleBase',
        'shipping': 'ShippingModuleBase',
        'design': 'DesignModuleBase',
        'general': 'BaseModule'
    }
    base_class = base_class_map.get(args.type, 'BaseModule')
    
    builder.create_module_py(base_class)
    builder.create_init_py()
    builder.create_requirements_txt(args.dependencies or [])
    builder.create_readme_md()
    builder.create_template_files()
    builder.create_static_files()
    builder.create_migrations_init()
    
    # Build ZIP file
    zip_path = builder.build_zip(args.output_dir)
    
    # Cleanup
    if not args.keep_build:
        builder.cleanup()
    
    print(f"\n✅ Module '{args.module_name}' built successfully!")
    print(f"📦 ZIP file: {zip_path}")
    print(f"📋 Module type: {args.type}")
    print(f"📝 Ready for upload to the module system")


if __name__ == '__main__':
    main() 