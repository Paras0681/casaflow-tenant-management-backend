from django.db import models
from apps.users.models import Account


class Payments(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    uploaded_by = models.CharField(max_length=30, null=True, blank=True)
    invoice_id = models.CharField(max_length=10, null=True, blank=True)
    payment_utr = models.CharField(max_length=50, null=True, blank=True)
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    payment_receipt_url = models.URLField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateField(blank=False, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
    def __str__(self):
        return f"Payment of {self.amount} - {self.payment_id} by {self.account.first_name} - {self.account.phone_number}"
