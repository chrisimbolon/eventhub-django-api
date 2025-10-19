# backend/apps/users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'
    
    def ready(self):
        """
        Import signals when app is ready
        """
        # If you add signals later, import them here
        # import apps.users.signals
        pass