from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# ── Dev: allow ALL origins so the booking form works on any local port ──
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:5501',
    'http://127.0.0.1:5501',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Use console email backend in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Dev Logging — prints chatbot AI debug info to terminal ──
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'chatbot': {
            'format': '[CHATBOT] %(message)s',
        },
        'standard': {
            'format': '%(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'chatbot',
        },
    },
    'loggers': {
        'glow_guide.chatbot': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers':  ['console'],
            'level':     'INFO',
            'propagate': False,
        },
    },
}
