#!/bin/bash

echo "=== PostgreSQL Connection Fix Script ==="

# 1. Kill any hanging Django processes that might hold DB connections
echo "1. Killing Django processes that might hold database connections..."
pkill -f "manage.py runserver" || true
pkill -f "python.*manage.py" || true

# 2. Check PostgreSQL status
echo "2. Checking PostgreSQL status..."
sudo systemctl status postgresql --no-pager -l

# 3. Show current database connections
echo "3. Checking current database connections..."
sudo -u postgres psql -c "SELECT count(*) as total_connections FROM pg_stat_activity;"
sudo -u postgres psql -c "SELECT datname, usename, application_name, state FROM pg_stat_activity WHERE state = 'active';"

# 4. Show PostgreSQL connection settings
echo "4. Checking PostgreSQL connection limits..."
sudo -u postgres psql -c "SHOW max_connections;"
sudo -u postgres psql -c "SHOW superuser_reserved_connections;"

# 5. Kill idle connections (be careful with this!)
echo "5. Terminating idle connections..."
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';"

# 6. Restart PostgreSQL if needed
echo "6. Would you like to restart PostgreSQL? (y/n)"
read -r restart_postgres
if [ "$restart_postgres" = "y" ]; then
    sudo systemctl restart postgresql
    echo "PostgreSQL restarted."
fi

# 7. Try to start Django again
echo "7. Attempting to start Django server..."
cd /var/www/misamisa.pl
source venv/bin/activate
python manage.py check --database default

echo "=== Fix script completed ==="
echo "Try starting the Django server now with: bash start_server.sh" 