# Misamisa.pl - Django E-commerce Platform

A modern Django-based e-commerce platform with a modular architecture, built with Django, HTMX, and Vite for frontend asset management.

## 🚀 Features

- **E-commerce**: Product catalog, shopping cart, checkout, order management
- **User Management**: Registration, authentication, address management
- **Admin Interface**: Module management, product administration
- **Modern Frontend**: HTMX for dynamic interactions, Vite for asset building
- **Responsive Design**: Mobile-first approach with theme switching
- **Modular Architecture**: Pluggable modules system

## 🛠️ Tech Stack

- **Backend**: Django 4.x, Python 3.x
- **Frontend**: HTMX, Vanilla JavaScript
- **Styling**: SCSS with 7-1 architecture
- **Build Tool**: Vite for asset compilation
- **Database**: PostgreSQL (recommended)
- **Deployment**: Podman-ready

## 📁 Project Structure

```
misamisa.pl/
├── static/
│   ├── src/
│   │   ├── scss/          # SCSS source files (7-1 pattern)
│   │   └── js/            # JavaScript source files
│   ├── dist/              # Compiled assets (generated)
│   └── assets/            # Static assets (images, etc.)
├── templates/             # Django templates
├── shop/                  # E-commerce app
├── accounts/              # User management app
├── modules/               # Pluggable modules
├── downloads/             # File downloads app
└── config/               # Django settings
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd misamisa.pl
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Node.js dependencies**
   ```bash
   cd static
   npm install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

## 🛠️ Development

### Starting the Development Server

1. **Start Django development server**
   ```bash
   python manage.py runserver
   ```

2. **Start Vite dev server** (in another terminal)
   ```bash
   cd static
   npm run dev
   ```

3. **Visit the site**
   - Main site: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Frontend Development

- **SCSS files**: `static/src/scss/` (7-1 pattern)
- **JavaScript files**: `static/src/js/`
- **Compiled assets**: `static/dist/` (auto-generated)

### Building for Production

```bash
# Build frontend assets
cd static
npm run build

# Collect static files
python manage.py collectstatic

# Run production server
python manage.py runserver --settings=config.settings.production
```

## 📚 Key Concepts

### SCSS Architecture (7-1 Pattern)
```
static/src/scss/
├── abstracts/     # Variables, mixins, functions
├── base/          # Reset, typography, base styles
├── components/    # Reusable UI components
├── layout/        # Header, footer, grid, sidebar
├── utilities/     # Helper classes
├── themes/        # Theme variations
└── main.scss      # Main entry point
```

### Module System
- **Pluggable modules** in `modules/` directory
- **Module management** via admin interface
- **Dynamic loading** of module functionality

### HTMX Integration
- **Dynamic page updates** without full reloads
- **Form submissions** with real-time feedback
- **Navigation** with smooth transitions

## 🎨 Static Assets Management

### Directory Structure

```
/static/
├── .gitignore                      # Ignore compiled CSS, maps, etc.
├── package.json                    # Dependencies and build scripts
├── favicon.ico                     # Site favicon
│
├── dist/                           # Compiled/built assets (ignored by Git)
│   ├── css/
│   │   ├── mainStyle.css           # Compiled Frontend CSS (66KB)
│   │   └── adminStyle.css          # Compiled Admin CSS (3.9KB)
│   └── js/
│       ├── main.js                 # Bundled frontend JS (9.6KB)
│       ├── shop.js                 # Shop-specific JS (2.4KB)
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
│       │   ├── theme-toggle.js     # Dark/light theme toggle (45 lines)
│       │   ├── notifications.js    # Notification system (123 lines)
│       │   ├── user-menu.js        # User menu functionality (55 lines)
│       │   ├── dropdown-management.js # Dropdown management (141 lines)
│       │   ├── htmx-navigation.js  # HTMX navigation handling (296 lines)
│       │   ├── forms.js            # Enhanced form behavior (1 line - empty)
│       │   ├── tabs.js             # Tab switching (1 line - empty)
│       │   └── dropdown.js         # Dropdown functionality (1 line - empty)
│       ├── pages/                  # Page-specific JavaScript
│       │   ├── shop.js             # Shop page functionality (135 lines)
│       │   ├── products.js         # Product page features (1 line - empty)
│       │   ├── contact.js          # Contact form handling (1 line - empty)
│       │   └── home.js             # Homepage functionality (1 line - empty)
│       ├── admin/                  # Admin-specific JavaScript
│       │   └── productimage_single_primary.js # Product image handling (19 lines)
│       └── main.js                 # Frontend entry point
│
└── assets/                         # Static assets (not processed)
    └── images/                     # Images organized by type
        ├── logos/                  # Logo files
        └── backgrounds/            # Background images
```

### Development Workflow

#### Watch Mode (Development)
Watch SCSS and JS files and automatically compile on changes:
```bash
cd static
npm run dev
```

This will:
- Watch all SCSS and JS files for changes
- Compile to expanded CSS and JS (easier to debug)
- Generate source maps for debugging

#### Production Build
For production, use compressed CSS:
```bash
cd static
npm run build
```

#### Available Commands

| Command | Description |
|---------|-------------|
| `npm install` | Install Node.js dependencies |
| `npm run build` | Build compressed CSS and JS |
| `npm run dev` | Watch and compile expanded CSS (debugging) |
| `npm run clean` | Remove compiled files |
| `npm run build-css` | Build only CSS files |

### Integration with Django

The compiled assets are served by Django's static file handling:

1. Run `python manage.py collectstatic` in production
2. Include assets in your templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'dist/css/mainStyle.css' %}">
<script src="{% static 'dist/js/main.js' %}"></script>
```

### Best Practices

1. **Use CSS Custom Properties** for theming
2. **Organize by feature** - each major feature gets its own SCSS module
3. **Use semantic class names** - descriptive and meaningful
4. **Keep nesting shallow** - avoid deep nesting (max 3-4 levels)
5. **Comment your code** - especially for complex layouts
6. **Mobile-first** - design for mobile, then enhance for desktop
7. **Optimize images** - use appropriate formats and sizes

### Troubleshooting

#### CSS/JS Not Updating
- Make sure to run `npm run build` after SCSS/JS changes
- Check that import paths are correct in main SCSS files
- Verify compiled CSS and JS files exist in `dist/css/` and `dist/js/`

#### Build Errors
- Check SCSS syntax (missing semicolons, brackets, etc.)
- Check JavaScript syntax and imports
- Verify import paths are correct in both SCSS and JS files
- Look for undefined variables or mixins in SCSS
- Make sure all dependencies are installed

#### Performance
- Use compressed CSS and JS in production: `npm run build`
- Consider using source maps only in development
- Optimize images and other assets

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Development mode
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Database connection
- `STATIC_URL`: Static files URL
- `MEDIA_URL`: Media files URL

### Vite Configuration
- **Entry points**: Defined in `vite.config.js`
- **Output**: Compiled to `static/dist/`
- **Hot reload**: Available during development

## 🚀 Deployment

### Podman (Recommended)
```bash
podman-compose up -d
```

### Manual Deployment
1. Build frontend assets: `cd static && npm run build`
2. Collect static files: `python manage.py collectstatic`
3. Run migrations: `python manage.py migrate`
4. Start production server

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## 🆘 Support

- **Email**: oskar@pansol.pl