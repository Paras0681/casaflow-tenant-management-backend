import os
from decouple import config
# Default to dev settings, but allow override with DJANGO_SETTINGS_MODULE
django_env = config("DJANGO_ENV", default="local")
env_setting = os.getenv("DJANGO_SETTINGS_MODULE",  f"tenant_management.settings.{django_env}")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env_setting)
