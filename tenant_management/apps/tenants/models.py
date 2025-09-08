from django.db import models
from apps.users.models import Account
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload as cloudinary_upload

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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
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
    file = CloudinaryField("file", folder="tenant_files")
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
        if self.file and hasattr(self.file, 'file'):
            # Build folder path dynamically: tenant_files/room_<room_number>
            folder_path = f"tenant_files/room_{self.room.room_number}"
            # Upload to Cloudinary with folder
            upload_result = cloudinary_upload(self.file.file, folder=folder_path)
            self.file = upload_result["secure_url"]
            self.public_id = upload_result['public_id']
            

        super().save(*args, **kwargs)
