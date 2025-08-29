from django.db import models
from apps.users.models import Account
# Create your models here.
class Bills(models.Model):
    PAYMENT_STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )
    tenant =  models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bills")
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_pdf = models.FileField(upload_to="invoices/")
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bills"
        verbose_name = "Bill"
        verbose_name_plural = "Bills"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Bill for {self.tenant.email} - {self.amount}"

class Payments(models.Model):
    tenant = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payments")
    payment_id = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "payments"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
    def __str__(self):
        return f"Payment of {self.amount} - {self.payment_id} by {self.tenant.first_name} - {self.tenant.phone_number}"