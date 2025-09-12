from django.db import models
from apps.users.models import Account
from datetime import datetime
import os
import cloudinary.uploader
import os
from datetime import datetime
from django.conf import settings
from firebase_admin import storage

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
    active_tenants = models.IntegerField(default=0)
    max_occupants = models.PositiveIntegerField(default=0)
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
        ("not_paid", "Not Paid"),
        ("partial", "Partial"),
        ("overdue", "Overdue"),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tenants_data")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="tenants")
    payment_status = models.CharField(max_length=10, choices=RENT_STATUS_CHOICES, default="unpaid")
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lightbill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_tenant_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_month = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenants_data"
        verbose_name = "Tenants Data"
        verbose_name_plural = "Tenants Data"
        ordering = ["-created_at"]


class TenantsFiles(models.Model):
    FILE_TYPE_CHOICES = (
        ("id_proof", "ID Proof"),
        ("driving_license", "Driving License"),
        ("aadhar_card", "Aadhar Card"),
        ("pan_card", "Pan Card"),
        ("lease_agreement", "Lease Agreement"),
        ("meter_reading", "Meter Reading"),
        ("light_bill", "Light Bill"),
        ("water_bill", "Water Bill"),
        ("Maintenance", "Maintenance"),
        ("payment_receipt", "Payment Receipt"),
        ("other", "Other"),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tenants_files")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="tenants_files")
    file_url = models.URLField(max_length=500, blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    unit_reading = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenants_files"
        verbose_name = "Tenants Files"
        verbose_name_plural = "Tenants Files"

    def save(self, *args, **kwargs):
        if hasattr(self, "_uploaded_file"):
            if self.file_type == "payment_receipt":
                folder_path = f"tenant_files/room_{self.room.room_number}/invoices"
            folder_path = f"tenant_files/room_{self.room.room_number}/uploads"
            
            # Force PNG extension for generated invoice images
            file_ext = ".png"

            month_str = datetime.now().strftime("%b").upper()
            base_name = f"INVOICE_{month_str}_{self.account.first_name.upper()}{file_ext}"

            upload_result = cloudinary.uploader.upload(
                self._uploaded_file,
                folder=folder_path,
                public_id=base_name.replace(" ", "_"),
                overwrite=True,
                use_filename=True,
                unique_filename=False,
                resource_type="image"  # explicitly set resource_type
            )
            self.file_url = upload_result["secure_url"]
            self.public_id = upload_result["public_id"]

        super().save(*args, **kwargs)

    def set_uploaded_file(self, file):
        """Attach file before saving"""
        self._uploaded_file = file
