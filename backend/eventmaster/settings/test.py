from .development import *

# Use SQLite for tests (faster and no permission issues!)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database (super fast!)
    }
}