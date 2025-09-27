"""
WSGI config for tenant_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from decouple import config

django_env = config("DJANGO_ENV", default="local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"tenant_management.settings.{django_env}")

application = get_wsgi_application()
