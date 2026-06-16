"""
MakuUP Studio — Django Base Settings
"""
import os
from decouple import config

# BASE DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECRET KEY
SECRET_KEY = config('DJANGO_SECRET_KEY', default='change-me-in-production')

# APPS
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',  # must be before staticfiles
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'app',
    'glow_guide',
]

# MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'makuup.urls'
WSGI_APPLICATION = 'makuup.wsgi.application'

# Dummy database — we use MongoEngine for all business data
# Django needs this minimal config for internal functioning
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

# MongoEngine connection — done in app/__init__.py
MONGODB_URI = config('MONGODB_URI', default='mongodb://localhost:27017/makuup_studio')
MONGODB_DB_NAME = config('MONGODB_DB_NAME', default='makuup_studio')

# Admin Credentials (stored in env — single user, no DB needed)
ADMIN_USERNAME = config('ADMIN_USERNAME', default='noor')
ADMIN_PASSWORD = config('ADMIN_PASSWORD', default='change-me')

# JWT Config
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default=60, cast=int)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = config('JWT_REFRESH_TOKEN_EXPIRE_DAYS', default=7, cast=int)
JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    config('FRONTEND_URL', default='http://localhost:5500'),
    'http://127.0.0.1:5500',
    'http://localhost:5500',
    'https://makuupstudio.web.app',
    'https://makuupstudio.firebaseapp.com',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# EMAIL (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='')
STUDIO_EMAIL = config('STUDIO_EMAIL', default='hello@makuupstudio.in')
STUDIO_OWNER_EMAIL = config('STUDIO_OWNER_EMAIL', default='')
STUDIO_NAME = config('STUDIO_NAME', default='MakuUP Studio')

# Twilio WhatsApp
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM', default='whatsapp:+14155238886')
STUDIO_WHATSAPP_TO = config('STUDIO_WHATSAPP_TO', default='whatsapp:+918299913988')

# Razorpay
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# Cloudinary
CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default='')

# Booking Settings
MAX_BOOKINGS_PER_DATE = config('MAX_BOOKINGS_PER_DATE', default=3, cast=int)

# Glow Guide AI
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Templates (minimal — only for any admin templates if needed)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]
