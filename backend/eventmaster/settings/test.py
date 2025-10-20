from .development import *

# Use SQLite for tests (faster and no permission issues!)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database (super fast!)
    }
}

# # full API routing for integration tests
# ROOT_URLCONF = "eventmaster.urls"
# INSTALLED_APPS += [
#     "apps.events",
#     "apps.users",
#     "apps.session_manager",
#     "apps.tracks",
# ]
