"""
ASGI config for tenant_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from decouple import config

django_env = config("DJANGO_ENV", default="local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"tenant_management.settings.{django_env}")
application = get_asgi_application()
