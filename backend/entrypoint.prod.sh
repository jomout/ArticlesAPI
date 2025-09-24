#!/usr/bin/env sh

set -e

echo "Running Django setup tasks."

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Add demo users
python manage.py load_demo_users || true

# Add demo articles
python manage.py load_demo_articles --username demo_user1 || true

# Create superuser
python manage.py createsuperuser --noinput || true

# Start ASGI server
echo "Starting Uvicorn."
exec python -m uvicorn app_api.asgi:application --host 0.0.0.0 --port 8000
