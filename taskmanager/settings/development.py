"""
Development settings for taskmanager project.
"""

from .base import *  # noqa: F403, F401
from .base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.azurewebsites.net']

# Database configuration is now in base.py using environment variables
# SQLite configuration removed - using PostgreSQL from .env

# Disable HTTPS requirements in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
