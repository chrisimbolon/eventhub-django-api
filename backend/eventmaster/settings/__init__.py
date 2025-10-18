"""
Settings package initialization.
"""
import os

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'eventmaster.settings.development')

if 'production' in settings_module:
    from .production import *
elif 'development' in settings_module:
    from .development import *
else:
    from .base import *
