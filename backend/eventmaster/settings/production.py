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
# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
# ALLOWED_HOSTS = ["127.0.0.1", "localhost", "eventhub.localhost", "backend"]
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


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
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://eventhub.app,https://api.eventhub.app"
).split(",")


# Trust X-Forwarded headers from Caddy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Enable HTTPS redirect and secure cookies
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# CSRF trusted origins (important for HTTPS)
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")



# -------------------------------------
# REST Framework + JWT
# -------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=30)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=7)

# -------------------------------------
# Logging (rotating file handler)
# -------------------------------------
# LOGGING["root"]["handlers"] = ["file"]
# LOGGING["root"]["level"] = "WARNING"
# LOGGING["loggers"]["django"]["level"] = "WARNING"
# LOGGING["handlers"]["file"]["filename"] = BASE_DIR / "logs" / "production.log"

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
