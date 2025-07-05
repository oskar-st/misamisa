#!/bin/bash

# Kill any existing Django processes
pkill -f "manage.py runserver" || true

# Change to project directory
cd /var/www/misamisa.pl

# Activate virtual environment and start server
source venv/bin/activate

# Check if database is accessible
echo "Checking database connection..."
if ! python manage.py check --database default; then
    echo "Database connection failed. This might be a PostgreSQL connection issue."
    echo "Try running: bash quick_fix.sh"
    echo "Or see POSTGRESQL_CONNECTION_FIX.md for detailed instructions."
    exit 1
fi

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 