from .base import *
from decouple import config

DEBUG = True

ALLOWED_HOSTS = [
    config("WEB_SERVICE_NAME", default=""),
    config("FRONTEND_STAGE_SERVICE", default=""),
]
CORS_ALLOWED_ORIGINS = [
    config("FRONTEND_STAGE_SERVICE", default=""),
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'OPTIONS': {'sslmode': 'require'},
    }
}
