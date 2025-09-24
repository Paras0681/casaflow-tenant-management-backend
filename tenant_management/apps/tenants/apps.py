from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenant_management.apps.tenants'

    def ready(self):
        import tenant_management.apps.tenants.signals