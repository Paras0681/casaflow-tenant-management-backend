from .base import *
from .base import BASE_DIR

dir_path = BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(dir_path, "db.sqlite3"),  # safer for import-time evaluation
    }
}