# Fix Admin Categories Issue

The categories admin is showing `TemplateDoesNotExist: django_mptt_admin/change_list.html` because the `django-mptt-admin` package is not installed.

## Quick Fix:

```bash
cd /var/www/misamisa.pl
source venv/bin/activate
pip install django-mptt-admin
```

Then uncomment in `config/settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps ...
    'mptt',  # Django MPTT for tree structures
    'django_mptt_admin',  # MPTT admin interface with drag & drop
    # ... other apps ...
]
```

Then restart the server:
```bash
python manage.py runserver 0.0.0.0:8000
```

The admin categories at `/admin/shop/category/` will then work with the drag-and-drop tree interface. 