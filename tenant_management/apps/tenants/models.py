from django.db import models
from apps.users.models import Account
# Create your models here.


class Property(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_floors = models.PositiveIntegerField(default=1)
    total_rooms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "properties"
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.name


class Room(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.PositiveIntegerField(unique=True)
    occupants = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "rooms"
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ["room_number"]

class TenantsData(models.Model):
    RENT_STATUS_CHOICES = (
        ("paid", "Paid"),  
        ("unpaid", "Unpaid"),
        ("pending", "Pending"),
        ("partial", "Partial"),
        ("overdue", "Overdue"),
    )

    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tenants_data")
    room_number = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="tenants")
    rent_status = models.CharField(max_length=10, choices=RENT_STATUS_CHOICES, default="unpaid")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lightbill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waterbill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenants_data"
        verbose_name = "Tenants Data"
        verbose_name_plural = "Tenants Data"
        ordering = ["-created_at"]
