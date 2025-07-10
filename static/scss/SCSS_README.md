# SCSS Setup for MisaMisa Shop

This project uses SCSS (Sass) for styling with a modular approach. All styles are organized in SCSS files and compiled to CSS using Python.

## Project Structure

```
static/
├── scss/
│   ├── style.scss                    # Main SCSS file (imports all modules)
│   ├── admin.scss                    # Django admin enhancements
│   └── modules/
│       └── _module-management.scss   # Module management styles
├── css/
│   └── style.css                     # Compiled CSS (generated)
└── admin/
    └── css/
        └── enhanced_tree_admin.css   # Compiled admin CSS (generated)
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Install Python dependencies:
```bash
make install
# or
pip install libsass
```

2. Build CSS for the first time:
```bash
make build
# or
npm run build-css
# or manually:
python -m sass static/scss/style.scss:static/css/style.css --style compressed
```

## Development Workflow

### Watch Mode (Recommended for Development)

Watch SCSS files and automatically compile on changes:

```bash
make dev
# or
python -m sass --watch static/scss/style.scss:static/css/style.css --style expanded
```

This will:
- Watch all SCSS files for changes
- Compile to expanded CSS (easier to debug)
- Generate source maps for debugging

### Production Build

For production, use compressed CSS:

```bash
make build
# or
python -m sass static/scss/style.scss:static/css/style.css --style compressed
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make build` | Build compressed CSS |
| `make watch` | Watch and compile compressed CSS |
| `make dev` | Watch and compile expanded CSS (debugging) |
| `make clean` | Remove compiled CSS files |
| `make setup` | Install dependencies and build CSS |

## SCSS Organization

### Main File: `static/scss/style.scss`

This is the main SCSS file that imports all other modules:

```scss
// Variables and global styles
:root {
  --background-color: #fffaf3;
  --text-color: #333;
  // ... more variables
}

// Import module styles
@import 'modules/module-management';
```

### Module Files: `static/scss/modules/`

Each feature has its own SCSS module:

- `_module-management.scss` - Module management interface styles

### Adding New SCSS Modules

1. Create a new file in `static/scss/modules/`:
```bash
touch static/scss/modules/_new-feature.scss
```

2. Add your styles:
```scss
// New Feature Styles
.new-feature {
  // Your styles here
}
```

3. Import in `static/scss/style.scss`:
```scss
@import 'modules/new-feature';
```

4. Rebuild CSS:
```bash
make build
```

## SCSS Features Used

### Variables
```scss
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
}
```

### Nesting
```scss
.module-card {
  background: white;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  .module-title {
    font-weight: bold;
  }
}
```

### Mixins (if needed)
```scss
@mixin button-style($bg-color, $text-color) {
  background: $bg-color;
  color: $text-color;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
}

.btn-primary {
  @include button-style(#007bff, white);
}
```

## CSS Custom Properties (CSS Variables)

The project uses CSS custom properties for theming:

```scss
:root {
  --background-color: #fffaf3;
  --text-color: #333;
  --accent-color: #d77e00;
}

html[data-theme="dark"] {
  --background-color: #1a1a1a;
  --text-color: #f0f0f0;
  --accent-color: #ff9d2d;
}
```

## Integration with Django

The compiled CSS is automatically served by Django's static file handling. Make sure to:

1. Run `python manage.py collectstatic` in production
2. Include the CSS in your templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

## Admin Styles

The project includes enhanced Django admin styles for the category tree management:

- **Source**: `static/scss/admin.scss`
- **Compiled to**: `static/admin/css/enhanced_tree_admin.css`
- **Features**: Enhanced MPTT tree interface with drag & drop, visual feedback, and color-coded levels

The admin styles are automatically compiled when running `npm run build-css` and included in the Django admin via the `CategoryAdmin.Media` class.

## Troubleshooting

### CSS Not Updating
- Make sure to run `npm run build-css` after SCSS changes
- For development, you can use `make dev` for the main styles  
- Check that the import path is correct in `style.scss`
- Verify the compiled CSS files exist: `static/css/style.css` and `static/admin/css/enhanced_tree_admin.css`
- Run `python manage.py collectstatic` if serving static files

### SCSS Compilation Errors
- Check SCSS syntax (missing semicolons, brackets, etc.)
- Verify import paths are correct
- Look for undefined variables or mixins
- Make sure `libsass` is installed: `pip install libsass`

### Performance
- Use compressed CSS in production: `make build`
- Consider using source maps only in development
- Optimize images and other assets separately

## Best Practices

1. **Use CSS Custom Properties** for theming and consistent values
2. **Organize by feature** - each major feature gets its own SCSS module
3. **Use semantic class names** - descriptive and meaningful
4. **Keep nesting shallow** - avoid deep nesting (max 3-4 levels)
5. **Comment your code** - especially for complex layouts or calculations
6. **Test in both themes** - light and dark mode
7. **Mobile-first** - design for mobile, then enhance for desktop

## Example Workflow

```bash
# Initial setup
make dev-setup

# Start development
make dev          # Terminal 1: Watch SCSS
make runserver    # Terminal 2: Django server

# Make changes to SCSS files
# CSS will automatically recompile

# For production
make build
make collectstatic
```

## Manual Commands

If you prefer to run commands manually instead of using Make:

```bash
# Install dependencies
pip install libsass

# Build once
python -m sass static/scss/style.scss:static/css/style.css --style compressed
``` 