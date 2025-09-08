from rest_framework import serializers
from apps.users.models import Account, User
from .models import TenantsData, TenantsFiles, Room
from .utils.pdf_generator import save_invoice_for_tenant
import os
from django.conf import settings

class TenantsProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = Account
        fields = ['account_id', 'email', 'first_name', 'last_name', 'phone_number', 'occupation', 'lease_start_date', 'address', 'room_number']
    
    def create(self, validated_data): 
        user = User.objects.get(email=self.context['request'].user.email)
        account = Account.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            occupation=validated_data['occupation'],
            lease_start_date=validated_data['lease_start_date'],
            address=validated_data['address'],
            room_number=validated_data['room_number']
        )
        return account
    
class TenantsFilesSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    class Meta:
        model = TenantsFiles
        fields = [
            "id",
            "room",
            "room_number",
            "file",
            "file_type",
            "description",
            "unit_reading",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at", "room_number"]


class TenantsDataSerialzier(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = TenantsData
        fields = [
            "id",
            "rent_amount",
            "room_number",
            "lightbill_amount",
            "other_charges",
            "total_amount",
            "payment_status",
            "paid_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "paid_at"]

    def create(self, validated_data):
        user = self.context['request'].user
        account = Account.objects.get(user=user)
        room_number = self.context['request'].data.get('room_number')
        room = Room.objects.filter(room_number=room_number).first()
        if not room:
            raise serializers.ValidationError("Invalid room number.")
        accounts = Account.objects.filter(room_number=room_number)
        if not accounts.exists():
            raise ValueError("Please check your room number.") 
        for account in accounts:
            room = Room.objects.filter(room_number=account.room_number).first()
            save_invoice_for_tenant(
                account, 
                validated_data, 
                qr_code_path=os.path.join(settings.BASE_DIR, "static", "images", "qr_code.png").replace("\\", "/")
            )
            tenants_data = TenantsData.objects.create(**validated_data, account=account, room=room)
            return tenants_data