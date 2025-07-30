# Static Assets Structure

This directory contains all static assets for the MisaMisa project, organized using Vite for modern build process with SCSS compilation and asset optimization.

## Directory Structure

```
/static/
├── .gitignore                      # Ignore compiled CSS, maps, etc.
├── README.md                       # This file - build instructions, conventions
├── MIGRATION_SUMMARY.md            # Migration documentation
├── package.json                    # Dependencies and build scripts
├── favicon.ico                     # Site favicon
│
├── dist/                           # Compiled/built assets (ignored by Git)
│   ├── css/
│   │   ├── mainStyle.css           # Compiled Frontend CSS
│   │   └── adminStyle.css          # Compiled Admin CSS
│   └── js/
│       ├── main.js                 # Bundled frontend JS
│       ├── shop.js                 # Shop-specific JS
│       └── admin/                  # Admin JS files
│
├── src/                            # Source files
│   ├── scss/                       # SCSS source files (7-1 pattern)
│   │   ├── abstracts/              # Variables, mixins, functions
│   │   │   ├── _variables.scss     # Global CSS variables and SCSS vars
│   │   │   ├── _mixins.scss        # Reusable mixins
│   │   │   ├── _functions.scss     # SCSS functions
│   │   │   └── _index.scss         # Forward all abstracts
│   │   ├── base/                   # Global styles (reset, typography, base)
│   │   │   ├── _reset.scss         # Normalize/reset styles
│   │   │   ├── _typography.scss    # Global font styles, headings
│   │   │   ├── _base.scss          # Base HTML element styles
│   │   │   └── _index.scss         # Forward all base styles
│   │   ├── components/             # Reusable UI components
│   │   │   ├── _buttons.scss       # Button styles
│   │   │   ├── _forms.scss         # Form elements
│   │   │   ├── _cards.scss         # Card components
│   │   │   ├── _alerts.scss        # Alert and notification styles
│   │   │   ├── _modals.scss        # Modal dialogs
│   │   │   ├── _tables.scss        # Table component styles
│   │   │   ├── _pagination.scss    # Pagination component styles
│   │   │   └── _index.scss         # Forward all components
│   │   ├── layout/                 # Structural styles (grid, header, footer)
│   │   │   ├── _header.scss        # Site header styles
│   │   │   ├── _footer.scss        # Site footer styles
│   │   │   ├── _sidebar.scss       # Sidebar navigation styles
│   │   │   ├── _navigation.scss    # Main navigation styles
│   │   │   ├── _grid.scss          # Grid system and layout utilities
│   │   │   └── _index.scss         # Forward all layout styles
│   │   ├── utilities/              # Utility classes and helpers
│   │   │   ├── _helpers.scss       # Helper classes and utilities
│   │   │   ├── _animations.scss    # Animation and transition utilities
│   │   │   └── _index.scss         # Forward all utility styles
│   │   ├── themes/                 # Theme-specific styles
│   │   │   ├── _dark.scss          # Dark theme styles
│   │   │   └── _index.scss         # Forward theme styles
│   │   ├── backup/                 # Backup files (existing)
│   │   ├── main.scss               # Main entry point (frontend)
│   │   └── admin.scss              # Admin entry point
│   │
│   └── js/                         # JavaScript source files
│       ├── lib/                    # Reusable JS libraries/utilities
│       │   ├── utils.js            # Utility functions
│       │   ├── api.js              # API communication
│       │   └── validation.js       # Form validation
│       ├── components/             # UI component JavaScript
│       │   ├── theme-toggle.js     # Dark/light theme toggle
│       │   ├── notifications.js    # Notification system
│       │   ├── user-menu.js        # User menu functionality
│       │   ├── dropdown-management.js # Dropdown management
│       │   ├── htmx-navigation.js  # HTMX navigation handling
│       │   ├── forms.js            # Enhanced form behavior
│       │   ├── tabs.js             # Tab switching
│       │   └── dropdown.js         # Dropdown functionality
│       ├── pages/                  # Page-specific JavaScript
│       │   ├── shop.js             # Shop page functionality
│       │   ├── products.js         # Product page features
│       │   ├── contact.js          # Contact form handling
│       │   └── home.js             # Homepage functionality
│       ├── admin/                  # Admin-specific JavaScript
│       │   └── productimage_single_primary.js # Product image handling
│       └── main.js                 # Frontend entry point
│
└── assets/                         # Static assets (not processed)
    └── images/                     # Images organized by type
        ├── logos/                  # Logo files
        └── backgrounds/            # Background images
```

## Getting Started

### Prerequisites

- Node.js 16+ (for Vite build tools)

### Installation

1. Install dependencies:
```bash
cd static
npm install
```

2. Build assets for the first time:
```bash
npm run build
```

## Development Workflow

### Watch Mode (Development)

Watch SCSS and JS files and automatically compile on changes:

```bash
npm run dev
```

This will:
- Watch all SCSS and JS files for changes
- Compile to expanded CSS and JS (easier to debug)
- Generate source maps for debugging

### Production Build

For production, use compressed CSS:

```bash
npm run build
```

### Available Commands

| Command | Description |
|---------|-------------|
| `npm install` | Install Node.js dependencies |
| `npm run build` | Build compressed CSS and JS |
| `npm run dev` | Watch and compile expanded CSS (debugging) |
| `npm run clean` | Remove compiled files |
| `npm run build-css` | Build only CSS files |

## SCSS Architecture (7-1 Pattern)

The SCSS structure follows the 7-1 pattern with organized partials and index files for clean imports.

### Directory Descriptions

**Abstracts (`abstracts/`)** - Contains all Sass tools and helpers used across the project
- `_variables.scss` - Global CSS variables and SCSS variables
- `_mixins.scss` - Reusable mixins for common patterns
- `_functions.scss` - Custom SCSS functions
- `_index.scss` - Forwards all abstract files

**Base (`base/`)** - Contains the boilerplate code for the project
- `_reset.scss` - Normalize/reset styles
- `_typography.scss` - Global font styles and typography rules
- `_base.scss` - Base HTML element styles
- `_index.scss` - Forwards all base styles

**Components (`components/`)** - Contains all reusable components
- `_buttons.scss` - Button styles and variants
- `_forms.scss` - Form elements and validation styles
- `_cards.scss` - Card component styles
- `_alerts.scss` - Alert and notification styles
- `_modals.scss` - Modal dialog styles
- `_tables.scss` - Table component styles
- `_pagination.scss` - Pagination component styles
- `_index.scss` - Forwards all component styles

**Layout (`layout/`)** - Contains all the major layout components
- `_header.scss` - Site header styles
- `_footer.scss` - Site footer styles
- `_sidebar.scss` - Sidebar navigation styles
- `_navigation.scss` - Main navigation styles
- `_grid.scss` - Grid system and layout utilities
- `_index.scss` - Forwards all layout styles

**Utilities (`utilities/`)** - Contains utility classes and helpers
- `_helpers.scss` - Helper classes and utilities
- `_animations.scss` - Animation and transition utilities
- `_index.scss` - Forwards all utility styles

**Themes (`themes/`)** - Contains theme-specific styles
- `_dark.scss` - Dark theme styles
- `_index.scss` - Forwards theme styles

**Main Files**
- `main.scss` - Main entry point for frontend styles (4,583 lines - to be refactored)
- `admin.scss` - Admin interface styles (222 lines - existing)

## JavaScript Organization

### Lib (`src/js/lib/`)
- `utils.js` - Utility functions (1 line - empty)
- `api.js` - API communication (1 line - empty)
- `validation.js` - Form validation (1 line - empty)

### Components (`src/js/components/`)
- `theme-toggle.js` - Dark/light theme toggle (45 lines)
- `notifications.js` - Notification system (123 lines)
- `user-menu.js` - User menu functionality (55 lines)
- `dropdown-management.js` - Dropdown management (141 lines)
- `htmx-navigation.js` - HTMX navigation handling (296 lines)
- `forms.js` - Enhanced form behavior (1 line - empty)
- `tabs.js` - Tab switching (1 line - empty)
- `dropdown.js` - Dropdown functionality (1 line - empty)

### Pages (`src/js/pages/`)
- `shop.js` - Shop page functionality (135 lines)
- `products.js` - Product page features (1 line - empty)
- `contact.js` - Contact form handling (1 line - empty)
- `home.js` - Homepage functionality (1 line - empty)

### Admin (`src/js/admin/`)
- `productimage_single_primary.js` - Product image handling (19 lines)

## Asset Organization

### Images (`assets/images/`)
- `logos/` - Logo files (SVG, PNG)
- `backgrounds/` - Background images

### Compiled Assets (`dist/`)
- `css/mainStyle.css` - Compiled frontend styles (66KB)
- `css/adminStyle.css` - Compiled admin styles (3.9KB)
- `js/main.js` - Bundled frontend JavaScript (9.6KB)
- `js/shop.js` - Shop-specific JavaScript (2.4KB)

## Integration with Django

The compiled assets are served by Django's static file handling:

1. Run `python manage.py collectstatic` in production
2. Include assets in your templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'dist/css/mainStyle.css' %}">
<script src="{% static 'dist/js/main.js' %}"></script>
```

## Best Practices

1. **Use CSS Custom Properties** for theming
2. **Organize by feature** - each major feature gets its own SCSS module
3. **Use semantic class names** - descriptive and meaningful
4. **Keep nesting shallow** - avoid deep nesting (max 3-4 levels)
5. **Comment your code** - especially for complex layouts
6. **Mobile-first** - design for mobile, then enhance for desktop
7. **Optimize images** - use appropriate formats and sizes

## Troubleshooting

### CSS/JS Not Updating
- Make sure to run `npm run build` after SCSS/JS changes
- Check that import paths are correct in main SCSS files
- Verify compiled CSS and JS files exist in `dist/css/` and `dist/js/`

### Build Errors
- Check SCSS syntax (missing semicolons, brackets, etc.)
- Check JavaScript syntax and imports
- Verify import paths are correct in both SCSS and JS files
- Look for undefined variables or mixins in SCSS
- Make sure all dependencies are installed

### Performance
- Use compressed CSS and JS in production: `npm run build`
- Consider using source maps only in development
- Optimize images and other assets 