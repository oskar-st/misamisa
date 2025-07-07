# Missing Dependencies Installation Guide

## Problem
The Django server is failing to start due to missing Python packages:
- `django-mptt` (for nested categories)
- `django-turnstile` (for form protection)

## Quick Fix

Run these commands in your terminal:

```bash
# Activate virtual environment
source venv/bin/activate

# Install missing dependencies
pip install django-mptt django-turnstile

# Or install all dependencies from requirements.txt
pip install -r requirements.txt
```

## After Installing Dependencies

1. **Uncomment the apps in `config/settings.py`:**
   
   Change this:
   ```python
   # 'mptt',  # Django MPTT for tree structures - install: pip install django-mptt
   # 'django_mptt_admin',  # MPTT admin interface  
   # 'turnstile',  # Cloudflare Turnstile - install: pip install django-turnstile
   ```
   
   To this:
   ```python
   'mptt',  # Django MPTT for tree structures
   'django_mptt_admin',  # MPTT admin interface
   'turnstile',  # Cloudflare Turnstile
   ```

2. **Uncomment Turnstile configuration in `config/settings.py`:**
   
   Change this:
   ```python
   # Cloudflare Turnstile Configuration (commented out until package is installed)
   # TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY')
   # TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY')
   ```
   
   To this:
   ```python
   # Cloudflare Turnstile Configuration
   TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY')
   TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY')
   ```

3. **Start the server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## What I Fixed

- ✅ Made imports conditional in `shop/models.py` (already had try/except)
- ✅ Made imports conditional in `accounts/forms.py` 
- ✅ Created `requirements.txt` with all dependencies
- ✅ Temporarily disabled apps in settings until packages are installed

## All Required Dependencies

The `requirements.txt` file contains:
- Django==5.2.2
- psycopg2-binary (PostgreSQL)
- Pillow (Images)
- django-mptt (Tree categories)
- django-turnstile (Form protection)
- stripe>=5.0.0 (Payments)
- python-dotenv (Environment variables) 