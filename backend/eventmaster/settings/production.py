"""
Production settings for EventMaster API
"""
import logging
import os
from datetime import timedelta

from .base import *

logger = logging.getLogger(__name__)

# -------------------------------------
# General
# -------------------------------------
DEBUG = False

# ALLOWED_HOSTS with smart fallback
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,eventhub.localhost,eventhub.chrisimbolon.dev,eventhub_backend,backend"
).split(",")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

# -------------------------------------
# Security
# -------------------------------------

# ✅ FIXED: Don't use a fallback for SECRET_KEY in production!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required in production!")

# ✅ REMOVED: SECURE_SSL_REDIRECT (Caddy handles SSL, this causes infinite redirect!)
# Caddy handles HTTPS, Django only sees internal HTTP traffic
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS (optional but recommended)
# SECURE_HSTS_SECONDS = 31536000  # Uncomment after confirming HTTPS works
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# -------------------------------------
# Database (PostgreSQL)
# -------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "eventhub_db"),
        "USER": os.getenv("POSTGRES_USER", "eventhub_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "eventhub_pass"),
        "HOST": os.getenv("POSTGRES_HOST", "eventhub_db"),  # ✅ FIXED fallback
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,  # ✅ ADDED: Connection pooling (better performance)
    }
}

# -------------------------------------
# Static and Media files
# -------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Future: Uncomment when switching to DO Spaces
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticRootS3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.getenv('SPACES_ACCESS_KEY')
# AWS_SECRET_ACCESS_KEY = os.getenv('SPACES_SECRET_KEY')
# AWS_STORAGE_BUCKET_NAME = os.getenv('SPACES_BUCKET_NAME')
# AWS_S3_ENDPOINT_URL = os.getenv('SPACES_ENDPOINT')

# -------------------------------------
# Email Configuration
# -------------------------------------
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv(
    'DEFAULT_FROM_EMAIL',
    'EventHub <noreply@eventhub.chrisimbolon.dev>'
)

# ✅ ADDED: Warn if email not configured
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    logger.warning(
        "EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not configured. "
        "Email sending will not work!"
    )

# -------------------------------------
# CORS
# -------------------------------------
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://eventhub.chrisimbolon.dev"
).split(",")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS if origin.strip()]

# ✅ Trust X-Forwarded headers from Caddy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF trusted origins
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
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",  # ✅ ADDED: Better format
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",  # ✅ ADDED: Use verbose format
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
        "django.request": {           # ✅ ADDED: Log all requests
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# -------------------------------------
# Performance (✅ ADDED)
# -------------------------------------
# Cache (use locmem for now, switch to Redis later)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# -------------------------------------
# Gunicorn health check endpoint (optional)
# -------------------------------------
if os.getenv("DJANGO_READINESS_PROBE", "False") == "True":
    HEALTH_CHECK_URL = "/health/"