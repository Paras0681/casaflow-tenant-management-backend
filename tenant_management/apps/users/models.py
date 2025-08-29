from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone

from .managers import UserManager

# Create your models here.
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]

    def __str__(self):
        return self.email


class Account(models.Model):
    gender_choices = (
        ("male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )
    user = models.OneToOneField(User, settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account")
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=gender_choices, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    occupation = models.CharField(max_length=20, blank=True, null=True)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"first_name: {self.first_name}, email: {self.user.email}, phone_number: {self.phone_number}"
