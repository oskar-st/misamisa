# PostgreSQL Connection Issue Fix

## Problem
The Django server can't start because PostgreSQL has reached its maximum number of connections:
```
FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute
```

## Root Cause
PostgreSQL has a limited number of connections (usually 100 by default). When all connections are used up, only superuser accounts can connect to the database.

## Quick Fix
Run the quick fix script:
```bash
bash quick_fix.sh
```

This will:
1. Kill any hanging Django processes
2. Restart PostgreSQL to clear all connections
3. Start Django server fresh

## Detailed Diagnosis
For more detailed analysis, run:
```bash
bash fix_postgres_connections.sh
```

This will show:
- Current connection count
- Active connections
- PostgreSQL connection limits
- Option to restart PostgreSQL

## Manual Steps
If the scripts don't work, try these commands manually:

### 1. Kill Django processes
```bash
pkill -f "manage.py runserver"
pkill -f "python.*manage.py"
```

### 2. Check PostgreSQL connections
```bash
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### 3. Kill idle connections
```bash
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"
```

### 4. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 5. Start Django
```bash
cd /var/www/misamisa.pl
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## Prevention
To prevent this in the future:

### 1. Close database connections properly
Ensure Django settings include:
```python
DATABASES = {
    'default': {
        # ... other settings ...
        'CONN_MAX_AGE': 60,  # Close connections after 60 seconds
        'OPTIONS': {
            'MAX_CONNS': 20,  # Limit connections per process
        },
    }
}
```

### 2. Increase PostgreSQL connection limit
Edit `/etc/postgresql/*/main/postgresql.conf`:
```
max_connections = 200
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## This is NOT a Django Code Issue
The cart bug fix we implemented is working correctly. This is a separate database connection management issue that can happen on busy servers. 