"""
Production settings for deployment on Render
"""
import os
import dj_database_url
from .settings import *

# Security Settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Allowed Hosts
ALLOWED_HOSTS = [
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Add your frontend domain to CORS
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend.vercel.app',
    'http://localhost:3000',
]

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - Use Render PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static Files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files (for Render)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Inference API URL (will be Render service URL)
INFERENCE_API_URL = os.environ.get('INFERENCE_API_URL', 'http://localhost:8001')

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# OpenWeatherMap
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')

# VAPID Keys for Push Notifications
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'mailto:admin@croply.app')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
