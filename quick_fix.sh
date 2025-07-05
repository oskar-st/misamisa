#!/bin/bash

echo "=== Quick PostgreSQL Fix ==="

# Kill Django processes that might be holding connections
pkill -f "manage.py runserver" || true
pkill -f "python.*manage.py" || true
echo "Killed Django processes."

# Restart PostgreSQL to clear connections
sudo systemctl restart postgresql
echo "Restarted PostgreSQL."

# Wait a moment for PostgreSQL to start
sleep 3

# Try starting Django
cd /var/www/misamisa.pl
source venv/bin/activate
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 