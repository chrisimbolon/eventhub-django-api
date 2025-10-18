# project/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Allow all CORS in development for easier local frontend integration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = []

# Use sqlite by default in dev unless DATABASE_URL provided in env
# (base.py already provides sqlite fallback)

# Development email backend (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
