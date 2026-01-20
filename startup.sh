#!/bin/bash

# Azure App Service startup script for Django application

echo "Starting Django application..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email=os.environ.get('ADMIN_EMAIL', 'admin@taskmanager.com'),
        password=os.environ.get('ADMIN_PASSWORD', 'changeme123')
    )
    print('Superuser created')
else:
    print('Superuser already exists')
END

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --access-logfile '-' --error-logfile '-' taskmanager.wsgi:application
