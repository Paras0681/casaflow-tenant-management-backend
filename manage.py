#!/usr/bin/env python
import os
import sys
from decouple import config


def main():
    """Run administrative tasks."""
    # Read environment (default = local)
    django_env = config("DJANGO_ENV", default="local")  # local | staging | production

    # Point Django to the correct settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"tenant_management.settings.{django_env}")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
