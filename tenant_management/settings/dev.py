from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS = [
    config("WEB_SERVICE_NAME", default=""),
    ".koyeb.app",
    "localhost",
    "127.0.0.1",
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'koyebdb',
        'USER': 'koyeb-adm',
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'OPTIONS': {'sslmode': 'require'},
    }
}
