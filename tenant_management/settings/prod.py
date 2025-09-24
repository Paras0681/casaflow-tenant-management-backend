from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = []

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
