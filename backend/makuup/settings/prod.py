from .base import *  # noqa
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='makuup-backend.up.railway.app',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Security headers for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files — use full manifest storage in production (collectstatic must have been run)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Real Gmail SMTP in production (set in base.py from env)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
