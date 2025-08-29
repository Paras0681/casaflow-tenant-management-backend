import os

# Default to dev settings, but allow override with DJANGO_SETTINGS_MODULE
env_setting = os.getenv("DJANGO_SETTINGS_MODULE", "tenant_management.settings.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env_setting)
