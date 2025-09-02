"""
Development settings for Django project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development specific settings
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_ALL_ORIGINS = True  # Only for development

# CSRF settings for development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# JWT settings for development
SIMPLE_JWT.update({
    'AUTH_COOKIE_SECURE': False,
    'AUTH_COOKIE_SAMESITE': "Lax",
})

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['authentication']['level'] = 'DEBUG'
LOGGING['loggers']['blog']['level'] = 'DEBUG'
