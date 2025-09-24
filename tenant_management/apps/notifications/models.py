from django.db import models
from tenant_management.apps.tenants.models import Account

# Create your models here.
class Notification(models.Model):
    notification_type = models.CharField(max_length=20, choices=(
        ("invoice", "Invoice"),
        ("payment", "payment"),
        ("file", "file"),
        ("forget_password", "Forget Password"),
        ("password_reset", "Password Reset"),
    ))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
