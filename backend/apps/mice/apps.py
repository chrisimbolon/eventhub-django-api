# apps/mice/apps.py
from django.apps import AppConfig


class MiceConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'apps.mice'
    label               = 'mice'
    verbose_name        = 'MICE Production Management'
