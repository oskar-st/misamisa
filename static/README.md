# Static Assets Structure

This directory contains all static assets for the MisaMisa project, organized using a modern build process with SCSS compilation and asset optimization.

## Directory Structure

```
/static/
├── .gitignore                      # Ignore compiled CSS, maps, etc.
├── README.md                       # This file - build instructions, conventions
│
├── dist/                           # Compiled/built assets (ignored by Git)
│   ├── css/
│   │   ├── main.css                # Compiled Frontend CSS
│   │   ├── main.css.map            # Source maps for debugging
│   │   ├── admin.css               # Compiled Admin CSS
│   │   └── admin.css.map
│   ├── js/
│   │   ├── main.js                 # Bundled frontend JS
│   │   ├── main.js.map
│   │   ├── admin.js                # Bundled admin JS
│   │   └── admin.js.map
│   └── images/                     # Optimized images (if using build process)
│
├── src/                            # Source files
│   ├── scss/                       # SCSS source files (7-1 pattern)
│   │   ├── abstracts/              # Variables, mixins, functions
│   │   ├── base/                   # Global styles (reset, typography, base)
│   │   ├── layout/                 # Structural styles (grid, header, footer)
│   │   ├── components/             # Reusable UI components
│   │   ├── utilities/              # Utility classes and helpers
│   │   ├── vendor/                 # Third-party CSS/SCSS
│   │   ├── themes/                 # Theme-specific styles
│   │   │   ├── front/              # Frontend theme
│   │   │   └── admin/              # Admin theme
│   │   ├── main.scss               # Main entry point (frontend)
│   │   └── admin.scss              # Admin entry point
│   │
│   └── js/                         # JavaScript source files
│       ├── lib/                    # Reusable JS libraries/utilities
│       ├── components/             # UI component JavaScript
│       ├── pages/                  # Page-specific JavaScript
│       ├── admin/                  # Admin-specific JavaScript
│       ├── vendor/                 # Third-party JavaScript
│       ├── main.js                 # Frontend entry point
│       └── admin.js                # Admin entry point
│
├── assets/                         # Static assets (not processed)
│   ├── images/                     # Images organized by type
│   │   ├── logos/                  # Logo files
│   │   ├── backgrounds/            # Background images
│   │   ├── icons/                  # Icon sets
│   │   ├── placeholders/           # Placeholder images
│   │   └── content/                # Content images
│   ├── fonts/                      # Font files
│   └── documents/                  # Static documents
│
├── config/                         # Build configuration
│   ├── webpack.config.js           # Webpack configuration (future)
│   ├── postcss.config.js           # PostCSS configuration (future)
│   └── babel.config.js             # Babel configuration (future)
│
└── package.json                    # Dependencies and build scripts
```

## Getting Started

### Prerequisites

- Node.js 16+ (for build tools)
- Python 3.7+ (for current SCSS compilation)

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

Watch SCSS files and automatically compile on changes:

```bash
npm run dev
```

This will:
- Watch all SCSS files for changes
- Compile to expanded CSS (easier to debug)
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

### Abstracts (`src/scss/abstracts/`)
- `_variables.scss` - Global CSS variables and SCSS vars
- `_mixins.scss` - Reusable mixins
- `_functions.scss` - SCSS functions
- `_index.scss` - Forward all abstracts

### Base (`src/scss/base/`)
- `_reset.scss` - Normalize/reset styles
- `_typography.scss` - Global font styles, headings
- `_base.scss` - Base HTML element styles
- `_index.scss` - Forward all base styles

### Layout (`src/scss/layout/`)
- `_grid.scss` - Grid system
- `_header.scss` - Site header
- `_footer.scss` - Site footer
- `_navigation.scss` - Main navigation
- `_index.scss` - Forward all layout styles

### Components (`src/scss/components/`)
- `_buttons.scss` - Button styles
- `_forms.scss` - Form elements
- `_cards.scss` - Card components
- `_modals.scss` - Modal dialogs
- `_index.scss` - Forward all components

### Utilities (`src/scss/utilities/`)
- `_spacing.scss` - Margin/padding utilities
- `_display.scss` - Display utilities
- `_text.scss` - Text utilities
- `_colors.scss` - Color utilities
- `_index.scss` - Forward all utilities

### Themes (`src/scss/themes/`)
- `front/` - Frontend theme styles
- `admin/` - Admin theme styles

## JavaScript Organization

### Lib (`src/js/lib/`)
- `utils.js` - Utility functions
- `api.js` - API communication
- `validation.js` - Form validation

### Components (`src/js/components/`)
- `dropdown.js` - Dropdown functionality
- `tabs.js` - Tab switching
- `forms.js` - Enhanced form behavior

### Pages (`src/js/pages/`)
- `home.js` - Homepage functionality
- `products.js` - Product page features
- `contact.js` - Contact form handling

### Admin (`src/js/admin/`)
- `dashboard.js` - Dashboard functionality
- `user-management.js` - User admin features
- `settings.js` - Settings page logic

## Asset Organization

### Images (`assets/images/`)
- `logos/` - Logo files (SVG, PNG)
- `backgrounds/` - Background images
- `icons/` - Icon sets organized by type
- `placeholders/` - Placeholder images
- `content/` - Content images (gallery, testimonials)

### Fonts (`assets/fonts/`)
- `primary/` - Primary font family
- `secondary/` - Secondary font family
- `icons/` - Icon fonts

## Integration with Django

The compiled assets are served by Django's static file handling:

1. Run `python manage.py collectstatic` in production
2. Include assets in your templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'dist/css/main.css' %}">
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

### CSS Not Updating
- Make sure to run `npm run build` after SCSS changes
- Check that import paths are correct in main SCSS files
- Verify compiled CSS files exist in `dist/css/`

### Build Errors
- Check SCSS syntax (missing semicolons, brackets, etc.)
- Verify import paths are correct
- Look for undefined variables or mixins
- Make sure all dependencies are installed

### Performance
- Use compressed CSS in production: `npm run build`
- Consider using source maps only in development
- Optimize images and other assets 