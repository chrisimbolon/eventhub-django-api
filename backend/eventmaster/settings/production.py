"""
Production settings for EventMaster API
"""
import os
from datetime import timedelta

from .base import *

# -------------------------------------
# General
# -------------------------------------
DEBUG = False

# ALLOWED_HOSTS with smart fallback
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,eventhub.localhost,eventhub.chrisimbolon.dev,eventhub_backend,backend"
).split(",")

# Remove any empty strings from split
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

# -------------------------------------
# Security
# -------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-production-key")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# -------------------------------------
# Database (PostgreSQL)
# -------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "eventhub_db"),
        "USER": os.getenv("POSTGRES_USER", "eventhub_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "eventhub_pass"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# -------------------------------------
# Static and Media files
# -------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------
# CORS
# -------------------------------------
CORS_ALLOW_CREDENTIALS = True

# CORS origins with fallback
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://eventhub.chrisimbolon.dev"
).split(",")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS if origin.strip()]

# Trust X-Forwarded headers from Caddy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF trusted origins with fallback
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", 
    "https://eventhub.chrisimbolon.dev"
).split(",")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]

# -------------------------------------
# REST Framework + JWT
# -------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=30)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=7)

# -------------------------------------
# Logging (Docker / stdout)
# -------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# -------------------------------------
# Gunicorn health check endpoint (optional)
# -------------------------------------
if os.getenv("DJANGO_READINESS_PROBE", "False") == "True":
    HEALTH_CHECK_URL = "/health/"