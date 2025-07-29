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
│   └── dist/              # Compiled assets (generated)
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
├── vendor/        # Third-party styles
└── themes/        # Theme variations
```

### Module System
- **Pluggable modules** in `modules/` directory
- **Module management** via admin interface
- **Dynamic loading** of module functionality

### HTMX Integration
- **Dynamic page updates** without full reloads
- **Form submissions** with real-time feedback
- **Navigation** with smooth transitions

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
1. Build frontend assets: `npm run build`
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