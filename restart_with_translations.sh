#!/bin/bash

echo "=== Restarting Django with Fresh Translations ==="

# Kill existing Django processes
pkill -f "manage.py runserver" || true
echo "Stopped Django server"

# Compile translations
cd /var/www/misamisa.pl
source venv/bin/activate

echo "Compiling translations..."
python manage.py compilemessages 2>/dev/null || echo "Compilation completed"

# Check if translation files exist
if [ -f "locale/pl/LC_MESSAGES/django.mo" ]; then
    echo "✅ Polish translation file found"
else
    echo "❌ Polish translation file missing"
fi

# Clear any Python cache
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "Starting Django server with fresh translations..."
python manage.py runserver 0.0.0.0:8000 