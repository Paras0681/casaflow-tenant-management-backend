from .base import *

DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tenant_db',
        'USER': 'tenant_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
